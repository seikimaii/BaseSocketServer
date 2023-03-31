import os
import PyInstaller.__main__

class PyInstallerWrapper:
    def __init__(self, script_path, output_dir, data_files=None, parameters=None):
        self.script_path = script_path
        self.output_dir = output_dir
        self.parameters = parameters or []
        self.data_files = data_files or []

    def compile(self):
        # Set PyInstaller arguments
        args = [
            '--name=GG',
            #'--onefile',
            # '--distpath={}'.format(self.output_dir),
            '--add-data=./Config/server.ini;Config'
            
        ]
        args.extend(self.parameters)
        if isinstance(self.script_path, list):
            args.extend(self.script_path)
        else:
            args.append(self.script_path)
        
        # Call PyInstaller
        PyInstaller.__main__.run(args)
        
if __name__ == '__main__':
    script_path = ['../tool_Module/ICSocketServer.py']
    output_dir = 'C:/Users/n1n0l/Documents/code_temp/tool_Module/MM'
    parameters = ['-F']#['--noconsole']
    
    py_installer = PyInstallerWrapper(script_path, output_dir, parameters=parameters)
    py_installer.compile()
