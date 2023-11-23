
import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import assignments
app = assignments.app

class TestApp(unittest.TestCase):

    # endpoint healthz should return 200 blank body
    def test_healthz(self):
        tester = app.test_client(self)
        response = tester.get('/healthz', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'')
        self.assertEqual(response.headers['cache-control'], 'no-cache, no-store, must-revalidate')

    # endpoint healthz with params should return 400 blank body
    def test_healthzParams(self):
        tester = app.test_client(self)
        response = tester.get('/healthz?args=1', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'')
        self.assertEqual(response.headers['cache-control'], 'no-cache, no-store, must-revalidate')
    
    # endpoint healthz with body should return 400 blank body
    def test_healthzBody(self):
        tester = app.test_client(self)
        response = tester.get('/healthz', data='{ "name":"John"}', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'')
        self.assertEqual(response.headers['cache-control'], 'no-cache, no-store, must-revalidate')

    # endpoint healthz with params and body should return 400 blank body
    def test_healthzBodyandParam(self):
        tester = app.test_client(self)
        response = tester.get('/healthz?args=10', data='{ "name":"John"}', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'')
        self.assertEqual(response.headers['cache-control'], 'no-cache, no-store, must-revalidate')
        
    # endpoint other than healthz should return 404 blank body 
    def test_healthx(self):
        tester = app.test_client(self)
        response = tester.get('/healthx', content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'')
        self.assertEqual(response.headers['cache-control'], 'no-cache')
        
    # # endpoint healthz with database server down should return 503 blank body
    # def test_healthz503(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/healthz', content_type='application/json')
    #     self.assertEqual(response.status_code, 503)
    #     self.assertEqual(response.data, b'')
    #     self.assertEqual(response.headers['cache-control'], 'no-cache, no-store, must-revalidate')

    # endpoint healthz with post should return 405 blank body
    def test_healthz_with_post(self):
        tester = app.test_client(self)
        response = tester.post('/healthz', content_type='application/json')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data, b'')

    # endpoint healthz with put should return 405 blank body
    def test_healthz_with_put(self):
        tester = app.test_client(self)
        response = tester.put('/healthz', content_type='application/json')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data, b'')

    # endpoint healthz with delete should return 405 blank body
    def test_healthz_with_delete(self):
        tester = app.test_client(self)
        response = tester.delete('/healthz', content_type='application/json')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data, b'')
    
    # endpoint healthz with patch should return 405 blank body
    def test_healthz_with_patch(self):
        tester = app.test_client(self)
        response = tester.patch('/healthz', content_type='application/json')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data, b'')

if __name__ == '__main__':
    unittest.main()