/* -*-c++-*- 
 *------------------------------------------------------------------------------
 *                                                                              
 *        openalea.container: utils package                                     
 *                                                                              
 *        Copyright 2006 INRIA - CIRAD - INRA                      
 *                                                                              
 *        File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>         
 *                                                                              
 *        Distributed under the Cecill-C License.                               
 *        See accompanying file LICENSE.txt or copy at                          
 *            http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html       
 *                                                                              
 *        OpenAlea WebSite : http://openalea.gforge.inria.fr                    
 *       
 *                                                                       
 *-----------------------------------------------------------------------------*/

#include "container/grid.h"
using namespace container;

#include <boost/python.hpp>
#include "export_iterator.h"
using namespace boost::python;

typedef PyCustomRange<Grid::iterator> grid_index_range;

void grid_constructor (const Grid& g, const object* shape) {
	tuple shape_tup=tuple(shape);
	int a=extract<int>(shape_tup[0]);
}

tuple grid_shape (const Grid& g) {
	Grid::coord_list shp=g.shape();
	list l;
	Grid::coord_list::iterator it;
	for(it=shp.begin();it!=shp.end();++it) {
		l.append(*it);
	}
	return tuple(l);
}

grid_index_range export_grid_iter (const Grid& grid) {
	return grid_index_range(grid.begin(),grid.end());
}

int grid_index (const Grid& g, tuple coords) {
	Grid::coord_list coords_vec(g.dim());
	for(int i=0;i<g.dim();++i) {
		coords_vec[i]=extract<int>(coords[i]);
	}
	return g.index(coords_vec);
}

tuple grid_coordinates (const Grid& g, int index) {
	Grid::coord_list coords=g.coordinates(index);
	return make_tuple(coords[0],coords[1],coords[2]);
}

void export_grid () {
	export_custom_range<Grid::iterator>("_PyGridIndexRange");

	class_<Grid>("Grid", "regular grid in multi-dimensional space")
		//.def( init<const Grid::tuple&> ())
		//.def("__init__",&grid_constructor)
		.def("dim",&Grid::dim,"dimension of space")
		.def("shape",&grid_shape,"number of cells in each dimension")
		.def("size",&Grid::size,"total number of cells in the grid")
		.def("__len__",&Grid::size,"total number of cells in the grid")
		.def("__iter__",&export_grid_iter,"iterate on all cells indexes")
		.def("index",&grid_index,"id of a specific cell in the grid")
		.def("coordinates",&grid_coordinates,"coordinates of a specific cell in the grid")
		.def("state",&Grid::state,"debug function");
}
