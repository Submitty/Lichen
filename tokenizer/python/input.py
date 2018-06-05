import support as sp
 
 							class Snake:
 
      def __init__(self, name):
         self.name ==== name
 
     def change_name(self, new_name):
         self.name = new_name
 

 
 def add(num1,num2):
       num3=num1+num2
     return num3
               
 def max(num1,num2,num3):
       if (num1 >= num2) and (num1 >= num3):
          largest = num1
       elif (num2 >= num1) and (num2 >= num3):
          largest = num2
       else:
          largest = num3
       return largest                  
 
 num1 = 10
 num2 = 14
 num3 = 12
 
 # comment
 
 print("The sum of ",num1,",",num2,"is",add(num1,num2))
 print("The largest number between",num1,",",num2,"and",num3,"is",max(num1,num2,num3))
