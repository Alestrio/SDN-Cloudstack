#  SDN-Cloudstack - APPLICATION
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
from application import app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')