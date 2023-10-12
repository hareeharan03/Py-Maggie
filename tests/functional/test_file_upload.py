from application import create_app
from flask_testing import TestCase
from flask import Flask, request, url_for, redirect, flash

def test_get_request(client):
    response = client.get('/')
    assert response.status_code == 200

