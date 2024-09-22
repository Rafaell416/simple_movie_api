from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder

app = FastAPI()
app.title = "Movie REST API"
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
  async def __call__(self, request: Request):
    auth = await super().__call__(request)
    data = validate_token(auth.credentials)
    if data["email"] != "admin@gmail.com":
      raise HTTPException(status_code=403, detail="Credentials are wrong")

class User(BaseModel):
  email: str
  password: str 


class Movie(BaseModel):
  id: Optional[int] = None
  title: str = Field(max_length=15, min_length=5, default="Movie Title")
  overview: str = Field(min_length=15, max_length=50, default="Movie description")
  year: int = Field(le=2022, default=2022)
  rating: float = Field(default=0, le=10, ge=1)
  category: str = Field(min_length=5, max_length=15)

  class Config:
    schema_extra = {
      "example": {
        "id": 1,
        "title": "Fast and Furious",
        "overview": "Angry guys in fast cars",
        "year": 2001,
        "cateogry": "action",
        "rating": 9.9
      }
    }

@app.get("/", tags=['home'])
def message():
  return HTMLResponse('<h1 style="font-size: 100px;">hello cosmos</h1>')

@app.post("/login",  tags=["auth"])
def login(user: User):
  if user.email == "admin@gmail.com" and user.password == "admin":
    token = create_token(user.model_dump())
  return JSONResponse(content=token, status_code=200)

@app.get("/movies", tags=["movies"], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
  db = Session()
  result = db.query(MovieModel).all()
  return JSONResponse(status_code=200, content=jsonable_encoder(result))

@app.get("/movies/{id}", tags=["movies"], response_model=Movie, status_code=200, dependencies=[Depends(JWTBearer())])
def get_movie(id: int = Path(ge=1, le=2000)) -> Movie:
  db = Session()
  result = db.query(MovieModel).filter(MovieModel.id == id).first()
  if not result:
    return JSONResponse(status_code=404, content={"message": "not found"}) 
  else:
    return JSONResponse(status_code=200, content=jsonable_encoder(result))

@app.get("/movies/", tags=["movies"], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie]:
  db = Session()
  result = db.query(MovieModel).filter(MovieModel.category == category).all()
  if not result:
    return JSONResponse(status_code=404, content={"message": "not found"})
  else:
    return JSONResponse(status_code=200, content=jsonable_encoder(result))

@app.post("/movies", tags=["movies"], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_movie(movie: Movie) -> dict:
  db = Session()
  new_movie = MovieModel(**movie.model_dump())
  db.add(new_movie)
  db.commit()
  return JSONResponse(content={"message": "Movie successfully added ✅"}, status_code=201)

@app.put("/movies/{id}", tags=["movies"], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def update_movie(id: int, updated_movie: Movie) -> dict:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
       return JSONResponse(status_code=404, content={"message": "not found"})
    else:
      result.title = updated_movie.title
      result.overview = updated_movie.overview
      result.year = updated_movie.year
      result.rating = updated_movie.rating
      result.category = updated_movie.category
      db.commit()
      return JSONResponse(content={"message": "Movie successfully updated ✅"}, status_code=200)
    
@app.delete("/movies/{id}", tags=["movies"], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def delete_movie(id: int) -> dict:
  db = Session()
  movie = db.query(MovieModel).filter(MovieModel.id == id).first()
  print(movie)
  if not movie:
    return JSONResponse(status_code=404, content={"message": "Movie not found"})
  else:
    db.delete(movie)
    db.commit()
  return JSONResponse(content={"message": "Movie successfully deleted ✅"}, status_code=200)