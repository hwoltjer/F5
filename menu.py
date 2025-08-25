import readchar
import getpass
from clear_console import clear

class menu():
    """Class responsible for user menu."""
    use_cache: bool = True
    cache_results: bool = True

    def __init__(self):
    
        self.main_menu()
        self.f5_menu()
        
        self.ADC_addresses = {
            '1' : '10.32.6.34',
            '2' : '10.32.6.35'
        }

    def main_menu(self):
        """Creates dictionary with user menu (action to take) and ADC environment to select."""

        self.main_menu_actions = {
            '1' : "F5",
            'q' : 'Exit.'
        }

    def f5_menu(self):
        """Creates dictionary with user menu (action to take)."""

        self.f5_menu_actions = {
            '1' : "create list of existing VIPS with corresponding backend nodes of all ADC's.",
            '2' : "create new vips from excel file",
            '3' : "remove vips from excel file",
            'q' : 'Exit.'
        }

        self.f5_menu_adc = {
            '1' : 'BIGIP01.HW.LAB',
            '2' : 'BIGIP02.HW.LAB'
        }

    def print_main_action_menu(self):
        """Prints out user menu and asks user to select one of options."""

        while True:
            clear()
            print("Choose your action:\n")
            for options in self.main_menu_actions.keys():
                print(f"[{options}] {self.main_menu_actions[options]}")
            select_action = readchar.readkey()
            if select_action in self.main_menu_actions.keys():
                return select_action

    def print_f5_action_menu(self):
        """Prints out user menu and asks user to select one of options."""

        while True:
            clear()
            print("Choose your action:\n")
            for options in self.f5_menu_actions.keys():
                print(f"[{options}] {self.f5_menu_actions[options]}")
            select_action = readchar.readkey()
            if select_action in self.f5_menu_actions.keys():
                return select_action
 
    def print_adc_menu(self):
        """Prints out proper ADC's to select menu and asks user to select one of options."""

        while True:
            clear()
            print('Select ADC:\n')
            for options in self.f5_menu_adc.keys():
                print(f"[{options}] {self.f5_menu_adc[options]}")
            select_adc = readchar.readkey()
            if select_adc in self.f5_menu_adc.keys():
                return select_adc

    def F5_user_action(self):
        """Asks user about action to take and executes it."""

        while True:
            user_action = self.print_F5_action_menu()
            if user_action == '1':
                self.F5_menu_actions()                
            elif user_action == 'q':
                quit()
            #self.objects.clear_only_user_input()

    def main_user_action(self):
        """Asks user about action to take and executes it."""

        while True:
            user_action = self.print_main_action_menu()
            if user_action == '1':
                self.F5_user_action()
            elif user_action == 'q':
                quit()

    def resume(self):
        """Asks user if program should be continued."""

        print("Continue? (y/n):\n")
        select_action = readchar.readkey()
        return select_action

    def select_user_action(self):
        """Asks user about action to take and executes it."""

        while True:
            user_action = self.menu.print_action_menu()
            if user_action == '1':
                self.objects.read_address_objects_to_create()
                self._check_objects_to_create_with_existing_objects()
            elif user_action == '2':
                self.objects.read_address_objects_to_add()
                self._check_objects_to_add_with_existing_objects()
            elif user_action == '3':
                self.objects.read_address_objects_to_add()
                self.objects.read_address_objects_to_create()
                self._check_objects_to_add_with_objects_to_create()
            elif user_action == '4':
                self.objects.read_address_obbjects_to_delete()
                self._check_objects_to_delete_with_existing_objects()
            elif user_action == 'h':
                print_help()
            elif user_action == 'b':
                return None
            elif user_action == 'q':
                quit()
            self.objects.clear_only_user_input()