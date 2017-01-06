from Qt import QtGui, QtWidgets

from openalea.image_wralea.gui.select_box_widget import SelectBoxWidget


qapp = QtWidgets.QApplication.instance()

if qapp:
	class DummyNode (object) :
		def set_input (self, *args) :
			pass

		def get_input(self, *args):
			pass

		def register_listener (self, *args) :
			pass



	w = SelectBoxWidget(DummyNode() )
	w.setPixmap(QtGui.QPixmap("4_ocean_currents.png") )

	w.show()
