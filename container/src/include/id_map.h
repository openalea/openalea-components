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

#ifndef __CONTAINER_UTILS_IDMAP_H__
#define __CONTAINER_UTILS_IDMAP_H__


#include <iostream>
#include <utility>
#include <map>
#include "container/id_generator.h"

namespace container {
#define MAP std::map<int,D>

	template <typename D>
	class MapIntKeyIterator {
	private:
		typedef typename MAP::iterator mapit;//for internal use only
		typedef MapIntKeyIterator<D> self;//for internal use only
	public:
		typedef int value_type;//the type of data returned when dereferenced
	public:
		mapit map_it;//map iterator
	public:
		MapIntKeyIterator() {}
		//blanck constructor used
		//because I don't know how to initialise
		//iterators in for llops otherwise
		//do not use
		//
		MapIntKeyIterator(const mapit& ref_it) : map_it(ref_it) {
		//copy ref_it inside self
			//map_it=ref_it;
		}

		~MapIntKeyIterator() {}

		D& data () const {
		//return the second argument of this iterator
			return map_it->second;
		}

		int operator* () const {
		//dereference operator
		//return first argument of the pair owned
		//by map_it
			return map_it->first;
		}

		self& operator++ () {
		//post increment operator
			map_it++;
			return *this;
		}

		self operator++ (int) const {
		//preincrement operator
			self ret=*this;
			++map_it;
			return ret;
		}

		bool operator== (const self& other) const {
		//comparaison operator
		//use comparaison operator of owned iterator
			return map_it == other.map_it;
		}
		bool operator!= (const self& other) {
		//comparaison operator
		//use comparaison operator of owned iterator
			return map_it != other.map_it;
		}

		//debug
		void state () const {}
	};

	template <typename D>
	class ConstMapIntKeyIterator {
	private:
		typedef typename MAP::const_iterator mapit;//for internal use only
		typedef ConstMapIntKeyIterator<D> self;//for internal use only
	public:
		typedef int value_type;//the type of data returned when dereferenced
	public:
		mapit map_it;//map iterator
	public:
		ConstMapIntKeyIterator() {}
		//blanck constructor used
		//because I don't know how to initialise
		//iterators in for llops otherwise
		//do not use
		//
		ConstMapIntKeyIterator(const mapit& ref_it) : map_it(ref_it) {
		//copy ref_it inside self
			//map_it=ref_it;
		}

		~ConstMapIntKeyIterator() {}

		const D& data () const {
		//return the second argument of this iterator
			return map_it->second;
		}

		int operator* () const {
		//dereference operator
		//return first argument of the pair owned
		//by map_it
			return map_it->first;
		}

		self& operator++ () {
		//post increment operator
			map_it++;
			return *this;
		}

		self operator++ (int) const {
		//preincrement operator
			self ret=*this;
			++map_it;
			return ret;
		}

		bool operator== (const self& other) const {
		//comparaison operator
		//use comparaison operator of owned iterator
			return map_it == other.map_it;
		}
		bool operator!= (const self& other) {
		//comparaison operator
		//use comparaison operator of owned iterator
			return map_it != other.map_it;
		}

		//debug
		void state () const {}
	};

	template <typename D>
	class IdMap : public MAP {
	public:
		typedef typename MAP::iterator iterator;//used to traverse all elements : iter of (int,D)
		typedef typename MAP::const_iterator const_iterator;//const version of previous iterator
		typedef typename MAP::value_type value_type;//type of data in this map
		typedef MapIntKeyIterator<D> key_iterator;//iterator on keys in the map : iter of int
		typedef ConstMapIntKeyIterator<D> const_key_iterator;//iterator on keys in the map : iter of int

	
	public:
		typedef IdGenerator::InvalidId InvalidId;//error thrown when playing with invalid ids

	private:
		IdGenerator id_generator;//generator used to create ids when not provided
		//set of methods that can not be used
		void swap (const IdMap<D>& map) {}
		D& operator[] (const int& key) {}

	public:
		//inheritance from map
		IdMap () {}
		//template <typename InputIterator>
		//IdMap(InputIterator f, InputIterator l); TODO

		IdMap (const MAP& ref) {
		//fill this map with values taken from ref
			for(iterator it=ref.begin();it!=ref.end();++it) {
				add(it->second,it->first);
			}
		}

		~IdMap () {}

		bool has_key (const int& key) {
		//test wether a key is inside the map
			return MAP::find(key)!=MAP::end();
		}
		std::pair<iterator,bool> insert (const value_type& x) {
		//try to insert a new (int,D) pair in the map
		//if the key is already in the map throw IdError
			int key = id_generator.get_id(x->first);
			return MAP::insert(x);
		}

		void erase (iterator pos) {
		//remove element at position pos
		//release the corresponding id
			id_generator.release_id(pos->first);
			MAP::erase(pos);
		}

		void erase (const int& key) {
		//remove element which id is key
		//if key not in the map
		//throw IdError
			id_generator.release_id(key);
			MAP::erase(key);
		}

		void clear () {
		//clear all elements from the map
		//and release all used ids
			id_generator.clear();
			MAP::clear();
		}
		//specific functions
		key_iterator key_begin () {
		//iterator on all key in the map
			return key_iterator(MAP::begin());
		}

		const_key_iterator key_begin () const {
		//iterator on all key in the map
			return const_key_iterator(MAP::begin());
		}

		key_iterator key_end () {
		//iterator on all keys in the map
			return key_iterator(MAP::end());
		}

		const_key_iterator key_end () const {
		//iterator on all keys in the map
			return const_key_iterator(MAP::end());
		}

		int add (const D& data) {
		//add a new element in the map
		//create a new id to be used as key
		//return the id used to store the data
			int key=id_generator.get_id();
			MAP::insert(typename IdMap<D>::value_type(key,data));
			return key;
		}

		int add (const D& data, const int& key) {
		//try to add a new element in th emap
		//using the provided id as a key
		//if key is already used throw IdError
			int used_key=id_generator.get_id(key);
			MAP::insert(typename IdMap<D>::value_type(used_key,data));
			return used_key;
		}

		const D& getitem (const int& key) {
		//return the value stored with key
			typename MAP::iterator it=MAP::find(key);
			if(it==MAP::end()) {
				throw InvalidId(key);
			}
			else {
				return it->second;
			}
		}

		void setitem (const int& key, const D& data) {
		//return the value stored with key
			try {
				id_generator.get_id(key);
				MAP::insert(typename IdMap<D>::value_type(key,data));
			}
			catch (IdGenerator::InvalidId) {
				MAP::operator[](key)=data;
			}
		}

		//debug function
		/*void state () const  {
		//print all elements in the map
			typename MAP::const_iterator it;
			for(it=MAP::begin();it!=MAP::end();++it) {
				std::cout << "key : " << it->first << " val : " << it->second << std::endl;
			}
			std::cout << "id gen" << std::endl;
			id_generator.state();
		}*/
	};

#undef MAP
};
#endif //__CONTAINER_UTILS_IDMAP_H__

