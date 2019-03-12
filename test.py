import os
from shutil import copyfile
from glob import glob

script_dir = os.path.dirname(__file__)
xml_path_src = os.path.join(script_dir, './parameters/')
xml_files_src = glob('{}*.xml'.format(xml_path_src))

print(xml_files_src)

for file in xml_files_src:
    xml_file_name = os.path.basename(file)
    copyfile(os.path.join(xml_path_src, xml_file_name), os.path.join(script_dir, xml_file_name))

xml_files_dst = glob('*.xml')
