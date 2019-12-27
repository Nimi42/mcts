from distutils.core import setup, Extension
from glob import glob

module1 = Extension('backend',
                    sources=[
                        './mcts/mcts.c',
                        './mcts/multiline/multiline.c',
                        './mcts/str_node_dict/str-node-dict.c'],
                    include_dirs=[
                        'mcts/include',
                        'mcts/str_node_dict/include',
                        'mcts/multiline/include'
                    ],
                    extra_compile_args=['-D DEBUG', '-D NULL_CHECKS'])
                    #extra_objects=['/home/nemo/PycharmProjects/mcts/mcts/str-node-dict.o'])

setup(name='PackageName',
      version='1.0',
      description='This is a demo package',
      ext_modules=[module1])
