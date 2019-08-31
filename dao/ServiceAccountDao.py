from dao.helper.DbHelper import DbHelper


class ServiceAccountDAO:
   __db = None;

   def __init__(self):
       self.__db = DbHelper()

   def getServiceAccount(self):
       return self.__db.query("SELECT * FROM serviceaccount", None).fetchall();

   def getServiceAccount_claim(self):
       return self.__db.query("SELECT * FROM serviceaccount_claim", None).fetchall();

   def putServiceAccount(self, id, name, status, created):
       self.__db.query("""
          INSERT INTO serviceaccount
          values(%s, %s, %s, %s)
       """, (id, name, status, created))
       self.__db.commit()

   def putServiceAccount_claim(self, id, name, claim, created):
       self.__db.query("""
          INSERT INTO serviceaccount_claim
          values(%s, %s, %s, %s)
       """, (id, name, claim, created))
       self.__db.commit()

   def getOneServiceAccount_claim(self, id):
        return self.__db.query("""
            SELECT * FROM serviceaccount_claim WHERE id = %s
        """, id)

   def getServiceAccount_claim(self):
        return self.__db.query("SELECT * FROM serviceaccount_claim", None)

   def getOneServiceAccount(self, id):
        return self.__db.query("""
            SELECT * FROM serviceaccount WHERE id = %s
        """, id)

   def getServiceAccount(self):
        return self.__db.query("SELECT * FROM serviceaccount", None)

   def updateServiceAccount(self, id, status):
       self.__db.query("""
         UPDATE serviceaccount 
         SET status=%s
         WHERE id=%s
         """, (status, id))

       self.__db.commit()

   ## IMPORTANT! Below functions will not be used. Just for test!
   def deleteServiceAccount(self, id):
       self.__db.query("""
                DELETE FROM serviceaccount 
                WHERE id=%s
                """, (id))

       self.__db.commit()

# if __name__ == '__main__':
    # serviceAccountDAO = ServiceAccountDAO()
    # serviceAccountDAO.updateServiceAccount('1234', 'registered', None)

