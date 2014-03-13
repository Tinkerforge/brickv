import os

imports = []
device_classes = []

for plugin in sorted(os.listdir('.')):
    if not os.path.isdir(os.path.join('.', plugin)):
        continue

    imports.append('from brickv.plugin_system.plugins.{0} import device_class as {0}\n'.format(plugin))
    device_classes.append('    {0},\n'.format(plugin))

f = open('__init__.py', 'wb')
f.writelines(imports)
f.write('\n')
f.write('device_classes = [\n')
f.writelines(device_classes)
f.write(']\n')
