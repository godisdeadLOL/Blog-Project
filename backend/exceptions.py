from fastapi import HTTPException

class NoUserException(HTTPException):
    def __init__(self) :
        super().__init__(status_code=404, detail="no_user")

class NoBoardException (HTTPException) :
    def __init__(self) :
        super().__init__(status_code=404, detail="no_board")

class NoPostException (HTTPException) :
    def __init__(self) :
        super().__init__(status_code=404, detail="no_post")
        
class NoCommentException (HTTPException) :
    def __init__(self) :
        super().__init__(status_code=404, detail="no_comment")
        
class WrongAccessException (HTTPException) :
    def __init__(self) :
        super().__init__(status_code=403, detail="wrong_access")
        
class UserBlockedException(HTTPException) :
    def __init__(self) :
        super().__init__(status_code=403, detail="user_blocked")