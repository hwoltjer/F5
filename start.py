import sys
from settings import Settings

if len(sys.argv) < 4:
    sys.exit(1)

# Mandatory arguments
request_type        = sys.argv[1]
request_method      = sys.argv[2]
request             = sys.argv[3]

#optional arguments
search_obj = sys.argv[4] if len(sys.argv) > 4 else None
debug               = True
app_name            = 'extractor'


def start(module):
    extractor = module(settings = Settings(app_name = app_name, log_debug = debug),  
                                    request_type = request_type,                              
                                    request_method = request_method,
                                    request = request,
                                    search_obj = search_obj,
                                    )
    extractor.generate()


def main():
    if request_type == 'ipam':
        from ipam import ipam as ipam_module
        start(ipam_module)
    elif request_type == 'f5':
        from f5 import f5 as f5_module
        start(f5_module)

if __name__ == '__main__':
    main()