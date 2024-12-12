conda create --name analytics python boto3
pip install langchain --index-url https://pypi.org/simple
pip install langchain-community --index-url https://pypi.org/simple
pip install -U langchain-aws --index-url https://pypi.org/simple
pip install streamlit --index-url https://pypi.org/simple
pip install anthropic --index-url https://pypi.org/simple
pip show boto3
pip show langchain
pip3 install flask-sqlalchemy --index-url https://pypi.org/simple
pip install pypdf --index-url https://pypi.org/simple
pip install faiss-cpu --index-url https://pypi.org/simple (or gpu) 

streamlit hello
aws configure list profile

How to run the code
streamlit run rag_frontend.py