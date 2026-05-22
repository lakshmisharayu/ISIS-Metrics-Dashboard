"""
ISIS Metrics Collector
Collects ISIS database metrics from Junos routers via SSH
"""

import logging
import xml.etree.ElementTree as ET
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError, RpcError
import yaml
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ISISCollector:
    """Collects ISIS metrics from Junos devices"""
    
    # ISIS metrics we're interested in
    METRICS = {
        'total_lsps': 'Total LSPs in database',
        'lsp_database_size': 'LSP Database Size (bytes)',
        'isis_nodes': 'Number of ISIS Nodes',
        'prefixes': 'Number of Prefixes',
        'database_overload': 'Database Overload Flag',
        'lsp_count_l1': 'L1 LSP Count',
        'lsp_count_l2': 'L2 LSP Count',
        'adjacencies': 'Total Adjacencies',
        'interfaces': 'ISIS Enabled Interfaces'
    }
    
    def __init__(self, config_file='config/devices.yml'):
        """Initialize collector with device configuration"""
        self.config_file = config_file
        self.devices_config = self._load_config()
        self.connections = {}
    
    def _load_config(self) -> Dict:
        """Load device configuration from YAML file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            logger.warning(f"Could not load config file: {str(e)}")
            return {}
    
    def get_configured_devices(self) -> List[str]:
        """Get list of configured device hostnames"""
        return list(self.devices_config.get('hosts', {}).keys())
    
    def _connect_to_device(self, device_name: str) -> Optional[Device]:
        """
        Establish SSH connection to Junos device
        Args:
            device_name: Device hostname or IP
        Returns:
            Device object or None if connection fails
        """
        try:
            if device_name in self.connections:
                if self.connections[device_name].connected:
                    return self.connections[device_name]
            
            device_config = self.devices_config.get('hosts', {}).get(device_name, {})
            
            if not device_config:
                logger.error(f"No configuration found for device: {device_name}")
                return None
            
            dev = Device(
                host=device_config.get('host', device_name),
                user=device_config.get('username'),
                password=device_config.get('password'),
                port=device_config.get('port', 22),
                timeout=device_config.get('timeout', 30)
            )
            
            dev.open()
            self.connections[device_name] = dev
            logger.info(f"Successfully connected to {device_name}")
            return dev
        
        except ConnectError as e:
            logger.error(f"Connection error for {device_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error connecting to {device_name}: {str(e)}")
            return None
    
    def test_connection(self, device_name: str) -> Dict:
        """Test SSH connection to device"""
        dev = self._connect_to_device(device_name)
        if dev:
            return {
                'device': device_name,
                'connected': True,
                'status': 'Connection successful'
            }
        return {
            'device': device_name,
            'connected': False,
            'status': 'Connection failed'
        }
    
    def collect_metrics(self, device_name: str) -> Optional[Dict]:
        """
        Collect ISIS metrics from device
        Executes: show isis database extensive
        """
        dev = self._connect_to_device(device_name)
        if not dev:
            return None
        
        try:
            # Execute RPC to get ISIS database
            rpc_response = dev.rpc.request_shell_execute(
                command='show isis database extensive'
            )
            
            # Parse XML response
            metrics = self._parse_isis_output(rpc_response)
            metrics['device'] = device_name
            metrics['timestamp'] = datetime.utcnow().isoformat()
            
            logger.info(f"Successfully collected metrics from {device_name}")
            return metrics
        
        except RpcError as e:
            logger.error(f"RPC error on {device_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error collecting metrics from {device_name}: {str(e)}")
            return None
    
    def _parse_isis_output(self, output) -> Dict:
        """
        Parse ISIS database output and extract metrics
        
        Args:
            output: Raw output from 'show isis database extensive'
        
        Returns:
            Dictionary of parsed metrics
        """
        metrics = {
            'total_lsps': 0,
            'lsp_database_size': 0,
            'isis_nodes': 0,
            'prefixes': 0,
            'database_overload': False,
            'lsp_count_l1': 0,
            'lsp_count_l2': 0,
            'adjacencies': 0,
            'interfaces': 0,
            'raw_output': str(output)
        }
        
        try:
            # Convert output to string if it's an XML element
            if hasattr(output, 'text'):
                output_text = output.text
            else:
                output_text = str(output)
            
            lines = output_text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Parse total LSPs
                if 'LSP Database' in line and 'entries' in line:
                    try:
                        metrics['total_lsps'] = int(line.split()[0])
                    except (ValueError, IndexError):
                        pass
                
                # Parse database size
                if 'Database size' in line:
                    try:
                        metrics['lsp_database_size'] = int(line.split()[-2])
                    except (ValueError, IndexError):
                        pass
                
                # Count L1 and L2 LSPs
                if 'L1' in line:
                    metrics['lsp_count_l1'] += 1
                if 'L2' in line:
                    metrics['lsp_count_l2'] += 1
                
                # Parse overload status
                if 'Overload' in line:
                    metrics['database_overload'] = True
            
            # Calculate additional metrics
            metrics['isis_nodes'] = (metrics['lsp_count_l1'] + metrics['lsp_count_l2']) // 2
            
            return metrics
        
        except Exception as e:
            logger.error(f"Error parsing ISIS output: {str(e)}")
            return metrics
    
    def disconnect_all(self):
        """Close all device connections"""
        for device_name, dev in self.connections.items():
            try:
                dev.close()
                logger.info(f"Disconnected from {device_name}")
            except Exception as e:
                logger.warning(f"Error disconnecting from {device_name}: {str(e)}")
        self.connections.clear()
