import compileall, os

class CompileData:
	def __init__():
		self.dir_name = "app"
		self.exempt = [
			"/userprofile/"
		]

	def generate_pyc(self):
		compileall.compile_dir(self.dir_name)

	def delete_all_py_files(self):
		pass




if __name__ == '__main__':

	compl = CompileData()
	compl.generate_pyc()
	compl.delete_all_py_files()