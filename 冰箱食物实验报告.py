class Fridge(object):
    items = {}
    
    
    def __init__(self,food_ingredient_dict):
        if type(food_ingredient_dict) == dict:
            self.items = food_ingredient_dict
        else :
            return TypeError
        
    
        
    def __add_multi(self,ingredient_name,quantity):
        if type(ingredient_name) == str:
            self.items[ingredient_name] = self.items.get("ingredient_name",0) + quantity
        else :
            return TypeError

    
        
    def add_one(self,food_ingredient_name):
         if type(food_ingredient_name) == str:
                self.items[food_ingredient_name] = self.items.get(food_ingredient_name,0) + 1
         else :
                return TypeError

    

    def add_many(self,food_ingredient_dict):
        if type(food_ingredient_dict) == dict:
            for key in food_ingredient_dict:
                self.items[key] = self.items.get(key,0) + food_ingredient_dict.get(key)
        else :
            return TypeError


    
    def has(self,food_ingredient_name):
        if type(food_ingredient_name) != str:
            return TypeError
        else :
            if food_ingredient_name in self.items:
                return True
            else :
                return False



    def has_various(self,food_ingredient_dict):
        if type(food_ingredient_dict) == dict:
            for key in food_ingredient_dict:
                if key not in self.items:
                    return NameError
                else :
                    if food_ingredient_dict.get(key)>self.items.get(key):
                        return False
        return True   



    def __get_multi(self,ingredient_name,quantity):
       if ingredient_name not in self.items:
           return False
       else :
          sum = self.items.get(ingredient_name) - quantity
          if sum > 0:
              self.items[ingredient_name] = sum
              return quantity
          elif sum == 0:
              del self.items[ingredient_name]#删除键值对
              return quantity
          else :
              return False



    def get_one(self,food_ingredient_name):
        if food_ingredient_name not in self.items:
           return False
        else :
          sum = self.items.get(food_ingredient_name) - 1
          if sum > 0:
              self.items[food_ingredient_name] = sum
              return 1
          elif sum == 0:
              del self.items[food_ingredient_name]#删除键值对
              return 1
          else :
              return False
    
    

    def get_many(self,food_ingredient_dict):
        if type(food_ingredient_dict) == dict:
            for key in food_ingredient_dict:
                if key not in self.items:
                    return NameError
                else :
                    if food_ingredient_dict.get(key) > self.items.get(key):
                        return False
                    elif food_ingredient_dict.get(key) == self.items.get(key):
                        del self.items[key]#删除键值对
                        print(self.items)
                        return self.items  
                    else :
                        self.items[key] = self.items.get(key) - food_ingredient_dict.get(key)
                        print(self.items)
                        return self.items  #全部满足，返回食材字典
        else :
            return False
    
    

    def get_ingredients(self,food):
        if type(food) == dict :
            result = self.get_many(self,food)
            print(result)


    def  Print(self):
        print(self.items) 
    

class Food(object):
    food_dict = {}

        
    def __init__(self,**kwargs):
        self.food_dict = kwargs
        
        

    def get_ingredients(self):
        return self.food_dict

a = {"包包白":3,"完美的猪皮":3,"毛肚":3,"大蒜":3}
b = {"辣椒":3}
d = {"完美的猪皮":3}

c = Fridge(a)
c.Print()
c.add_one("野胡萝卜")
c.Print()
c.get_many(d)
c.Print()
