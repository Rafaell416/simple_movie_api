from models.movie import Movie

class MovieService():
  def __init__(self, db) -> None:
    self.db = db

  def get_movies(self):
    result = self.db.query(Movie).all()
    return result

  def get_movie(self, id):
    result = self.db.query(Movie).filter(Movie.id == id).first()
    return result
  
  def get_movies_by_category(self, category):
    result = self.db.query(Movie).filter(Movie.category == category).all()
    return result

  def create_movie(self, movie):
    new_movie = Movie(**movie.model_dump())
    self.db.add(new_movie)
    self.db.commit()
    return

  def update_movie(self, id, data):
    result = self.db.query(Movie).filter(Movie.id == id).first()
    if result:
      result.title = data.title
      result.overview = data.overview
      result.year = data.year
      result.rating = data.rating
      result.category = data.category
      self.db.commit()
      return True 
    else:
      return False  

  def delete_movie(self, id):
    result = self.db.query(Movie).filter(Movie.id == id).first()
    if result:
      self.db.delete(result)
      self.db.commit()
      return True
    else:
      return False