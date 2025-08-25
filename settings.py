import logging
from pprint import pprint
import sys, os
import json
from datetime import datetime
from os import path, makedirs, mkdir
from utilities import verify_dir
from logging.handlers import RotatingFileHandler

TESTING = False 

# Excluded variables from saving and loading
EXCLUDED_VARS = ['time', 'testing', 'ipam_session', 'gso_session', 
                 'test_limit', 'report_dir', 'excel_filepath', 'workbook', 
                 'log', 'top_logger', '_log', 'app_name', 'version', 'password']

class Settings():

    def __init__(self,
                 app_name,
                 print_logs: bool = True,
                 log_debug: bool = False,
                 testing: bool = False,
                 ):
        
        self._testing = testing 
        self._log_debug = log_debug

        # Log the time the app started
        self._time = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Credentials for logging into devices
        self.username = None
        self.password = None
        
        # Variables storing the various files and directories we use
        self._output_dir = 'Output'
        self._logs_dir = path.join(self._output_dir, 'Logs')
        self._settings_file = path.join(self._output_dir, 'settings.json')
         
        # Set up the logger
        self._app_name = app_name
        self._print_logs = print_logs
        self._top_logger = self.setup_applevel_logger()
        self._log = logging.getLogger(__name__)
        
        # Prepare the environment and load defaults
        self.make_directories()
        self.load()

        # Get the version
        #self.get_version()
          
    def make_directories(self):
        self._log.debug('Making directories')
        verify_dir(self._output_dir)
        verify_dir(self._settings_file)
        verify_dir(self._logs_dir)
        
    def save(self):
        """Saves the currently used settings to a file. Omits private 
        variables (anythingprefixed with '_') and anything in the explicit
        EXCLUDED_VARS list.
        """
        
        if not self._testing:
            EXCLUDED_VARS.append('password')

        # Remove any private or excluded variables
        included_vars = {k: v for k, v in vars(self).items() if \
                         not k.startswith('_') and 
                         not k in EXCLUDED_VARS}

        with open(self._settings_file, 'w') as settingsFile:
            json.dump(included_vars, settingsFile, sort_keys=True, indent=4)


    def load(self) -> bool:
        """Loads a saved settings file. If no settings are found, return None.

        Returns:
            bool: True if the settings could be loaded
        """

        # Check if the file exists and else create it
        try:
            with open(self._settings_file, 'r') as settingsFile:
                settings = json.load(settingsFile)
        except IOError:
            return False

        # Save the loaded variables to this class
        for k, v in settings.items():
            if k not in EXCLUDED_VARS: 
                setattr(self, k, v)
                
        return True
    
    
    def get_version(self) -> str:
        if os.path.exists('.version'):
            self.version = open('.version', 'r').read()
            self._log.info(f'Running {self._app_name} version: ' + self.version)
            return self.version
        else:
            self._log.warn('No version file found.')
            return '0.0.0'


    def get_credentials(self):
        """Query the user for a username and password and saves it to the
        class variables.

        Returns:
            tuple: A tuple of (username, password)
        """
        self.username = 'api-ddi-bhr'
        self.password = '3lVlbb21puCFxT'
        return self.username, self.password

    def __str__(self):
        return '\n'.join("%s: %s" % item for item in vars(self).items())
    
    
    def setup_applevel_logger(self):
            
        logger = logging.getLogger(self._app_name)
        logger.setLevel(logging.DEBUG)

        if self._print_logs:
            formatter = logging.Formatter(
                '%(name)-22s: %(levelname)-8s %(message)s')
            sh = logging.StreamHandler(sys.stdout)
            if self._log_debug:
                sh.setLevel(logging.DEBUG)
            else:
                sh.setLevel(logging.INFO)
            sh.setFormatter(formatter)
            logger.propagate = False
            logger.addHandler(sh)

        # Make the log output directory
        file_name = path.join(self._logs_dir, self._app_name + '.log')
        if (os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Add file rotating handler, with level DEBUG
        
        rotatingHandler = RotatingFileHandler(
            filename=file_name, maxBytes=100000, backupCount=5)
        
        rotatingHandler.setLevel(logging.DEBUG)
        rotatingHandler.setFormatter(formatter)
        logger.addHandler(rotatingHandler)

        return logger