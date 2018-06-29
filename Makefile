clean_pyc:
	find `pwd` -name '*.pyc' -type f -delete

clean_swp:
	find `pwd` -name '*.swp' -type f -delete

pip_install:
	pip install -r requirements/base.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn --default-timeout=100
	easy_install pycrypto
