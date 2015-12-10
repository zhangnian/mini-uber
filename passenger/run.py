# -*- coding: utf-8 -*-

from app.uber import app

import sys

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8090, debug=True, threaded=False)