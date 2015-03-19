import os
from os import path
from shutil import rmtree
from glob import glob

def clean_directory (dir_name) :
	list_rep=[]
	for filename in os.listdir(dir_name) :
		filepath=path.join(dir_name,filename)
		if path.isdir(filepath) :
			list_rep.append(filepath)
		else :
			base,ext=path.splitext(filename)
			if ext=='.pyc' : 
				os.remove(filepath)
				print filepath
	
	for rep in list_rep : clean_directory(rep)

def clean_gui_files (dir_name) :
	for filename in glob(path.join(dir_name,"*_rc.py")) :
		os.remove(filename)
	for filename in glob(path.join(dir_name,"*_ui.py")) :
		if path.basename(filename) != "compile_ui.py" :
			os.remove(filename)

if __name__=='__main__' :
	clean_directory(".")
	clean_gui_files(path.join("src","svgdraw") )
	for name in ("build",
	             "dist",
	             "src/openalea",
	             "src/OpenAlea.svgdraw.egg-info") :
		try :
			rmtree(name)
		except OSError :
			print "%s not found" % name

