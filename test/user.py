from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def testCreateUser():
    print("Do test...")
    #test...