class Bitarray:

    def __init__(self, length):
        self.length = length
        self.matrix = {}
  


    def add_node_to_matrix(self, idnode):
        ini = [-1]*self.length
        self.matrix.update({idnode: ini})
        
    def update_array(self, inode, index, value):
        self.matrix[inode][index] = value
        

    def delete_array(self):
        dump = []
        for i in self.matrix:
            if(not self.matrix[i].__contains__(1)):
                dump.append(i)
        for i in dump:
            del self.matrix[i]


    def get_data(self, i1, index):
        return self.matrix[i1][index]


    def update_all(self, index, contacting):
        #print(index)
        for i in self.matrix:
            if(contacting.__contains__(i)):
                #print("in update all")
                self.update_array(i, index, 1)
                #print(self.matrix[i][index])
                
            else:
                self.update_array(i, index, 0)
                #print(self.matrix[i])
        #print("Matrix",self.matrix)


    
        
