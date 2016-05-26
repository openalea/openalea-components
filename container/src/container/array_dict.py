import numpy as np
from scipy import ndimage as nd

def isiterable(obj):
    try:
        iter(obj)
        return True
    except:
        return False

class array_dict:
	def __init__(self, values= np.array([]), keys = None):
		if isinstance(values,array_dict):
			from copy import deepcopy
			self._values = deepcopy(values._values)
			self._keys = deepcopy(values._keys)
			self._index = deepcopy(values._index)
		elif isinstance(values,dict):        
			self._values = np.array(values.values())
			self._keys = np.array(values.keys())
			#self._index = np.array(nd.sum(np.arange(len(values)),self._keys,index=np.arange(max(self._keys)+1)),int)
			self._index = np.zeros(self._keys.max()+1,int)
			self._index[self._keys] = np.arange(len(self._keys))
		elif isinstance(values,list) and isinstance(values[0],tuple):
			self._values = np.array(values)[:,1]
			self._keys = np.array(np.array(values)[:,0],int)
			#self._index = np.array(nd.sum(np.arange(len(values)),self._keys,index=np.arange(max(self._keys)+1)),int)
			self._index = np.zeros(self._keys.max()+1,int)
			self._index[self._keys] = np.arange(len(self._keys))
		else:
			self._values = np.array(values)
			if not keys is None: 
				assert len(keys) == len(values)
				self._keys = np.array(keys)
				#self._index = np.array(nd.sum(np.arange(len(values)),self._keys,index=np.arange(max(self._keys)+1)),int)
				self._index = np.zeros(self._keys.max()+1,int)
				self._index[self._keys] = np.arange(len(self._keys))
			else: 
				if len(values)>0:
					self._keys = np.arange(len(values))
					self._index = np.arange(len(values))
				else:
					self._keys = np.array([],int)
					self._index = np.array([],int)
	
	def __getitem__(self,key):
		if self._index[key] > 0:
			return self._values[self._index[key]]
		elif key in self._keys:
			return self._values[0]
		else:
			raise KeyError(str(key))
	
	def __setitem__(self,key, value):
		import numpy as np
		if key in self._keys:
			self._values[self._index[key]] = value
		else:
			newindex = len(self._values)
			self._keys = np.append(self._keys,np.array([key]),axis=0)
			if key<len(self._index):
				self._index[key] = newindex
			else:
				new_index = np.zeros(key+1,int)
				new_index[0:len(self._index)] = self._index
				new_index[key] = newindex
				self._index = new_index

			if len(self) == 0:
				self._values = np.array([value])
			else:
				self._values = np.append(self._values,np.array([value]),axis=0)
	
	def __delitem__(self, key):
		index = self._index[key]
		self._values = np.delete(self._values,index,axis=0)
		self._index[self._keys[index:]] -= 1
		self._keys = np.delete(self._keys,index,axis=0)
		self._index[key] = 0

	def __len__(self):
		return len(self._values)

	def __str__(self):
		self.dict_string = "{"
		for i,k in enumerate(self._keys):
			self.dict_string = self.dict_string+str(k)+": "+str(self._values[self._index[k]])
			if i < self._values.size-1 : 
				self.dict_string = self.dict_string+", "
		self.dict_string = self.dict_string+"}\n"
		return self.dict_string
	
	def __repr__(self):
		self.dict_string = "{"
		if len(self)<10:
			for i,k in enumerate(self._keys):
				self.dict_string = self.dict_string+str(k)+": "+str(self._values[i])
				if i < self._values.size-1 : 
					self.dict_string = self.dict_string+", "
		else:
			for i in xrange(3):
				self.dict_string = self.dict_string+str(self._keys[i])+": "+str(self._values[i])+","
			self.dict_string = self.dict_string+"..."
			for i in xrange(3):
				self.dict_string = self.dict_string+","+str(self._keys[len(self)-3+i])+": "+str(self._values[len(self)-3+i])
		self.dict_string = self.dict_string+"}\n"
		return self.dict_string

	def to_dict(self):
		return dict([(tuple(k),self._values[i]) if isiterable(k) else (k,self._values[i]) for i,k in enumerate(self._keys)])

	def values(self,keys=None):
		if keys is None:
			return self._values[self._index[self._keys]]
		else:
			if isinstance(keys,np.ndarray) and keys.dtype == np.dtype('O'):
				return np.array([self.values(k) for k in keys])
			else:
				return self._values[self._index[keys]]
	
	def keys(self) :
		return self._keys

	def items(self):
		return [(k,self._values[i]) for i,k in enumerate(self._keys)]

	def update(self,values,keys=None,ignore_missing_keys=True,erase_missing_keys=True):
		if keys is None or (len(keys) == len(self._keys) and (keys==self.keys()).all()):
			assert len(self) == len(values)
			self._values = values
		else:
			assert len(keys) == len(values)
			keys_to_assign = np.intersect1d(keys,self._keys)
			if len(keys_to_assign)!=len(keys):
				key_range = np.array(nd.sum(np.arange(keys.size),keys,index=keys_to_assign),int)
				self._values[self._index[keys_to_assign]] = values[key_range]
				if ignore_missing_keys:
					print "Warning : some keys were missing from dictionary! (values ignored)"
				else:
					print "Warning : missing keys were added to the dictionary!"
					missed_keys = np.array(tuple(set(keys).difference(set(self._keys))))
					newindex = np.arange(len(self._values),len(self._values)+len(missed_keys))
					self._keys = np.append(self._keys,missed_keys,axis=0)
					if missed_keys.max()<len(self._index):
						self._index[missed_keys] = newindex
					else:
						new_index = np.zeros(missed_keys.max()+1,int)
						new_index[0:len(self._index)] = self._index
						new_index[missed_keys] = newindex
						self._index = new_index
					key_range = np.array(nd.sum(np.arange(keys.size),keys,index=missed_keys),int)
					if len(self) == 0:
						self._values = np.array(values[key_range])
					else:
						self._values = np.append(self._values,values[key_range],axis=0)
			else:
				if len(keys_to_assign)!=len(self._keys) or (keys!=self.keys()).any():
					if erase_missing_keys:
						print "Warning : missing keys were erased from the dictionary!"
						self._values = values
						self._keys = np.array(keys)
						self._index = np.zeros(self._keys.max()+1,int)
						self._index[self._keys] = np.arange(len(self._keys))
					else:
						self._values[self._index[keys]] = values
				else:
					self._values[self._index[keys]] = values
					

	def delete(self,keys_to_delete):
		keys_to_delete = np.intersect1d(keys_to_delete,self._keys)
		if len(keys_to_delete)>0:
			indices_to_delete = self._index[keys_to_delete]
			self._values = np.delete(self._values,indices_to_delete,0)
			self._keys = np.delete(self._keys,indices_to_delete,0)
			self._index[keys_to_delete] = 0
			self._index[self._keys] = np.arange(len(self._keys))
	
	def has_key(self, key):
		return key in self._keys

	def itervalues(self):
		return self.to_dict().itervalues()

	def iterkeys(self):
		return self.to_dict().iterkeys()

	def iteritems(self):
		return self.to_dict().iteritems()

	def keys_where(self,criterion):
		if isinstance(criterion,str):
			return self._keys[np.where(eval('self._values'+criterion))]
		elif isinstance(criterion,tuple) & isinstance(criterion[0],str):
			expression = '(self._values'+criterion[0]+')'
			for c in criterion[1:]:
				expression += '& (self._values'+c+')'
			return self._keys()[np.where(eval(expression))]
		else:
			assert len(criterion) == len(self._keys)
			return self._keys[np.where(criterion)]

