import React, { Component } from 'react';
import axios from 'axios';
import './App.css';

axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";

class App extends Component {
  render() {
    return (
      <div className="App">
        <h1>Welcome to recboard</h1>
        <div>
          <button type="button" onClick={this.onClick}>Send GET :8000/board/ </button>
        </div>
      </div>
    );
  }

  onClick(ev) {
    console.log("Sending a GET API Call !!!");
    // axios.get('http://127.0.0.1:8000/board/create')
    axios.post('http://127.0.0.1:8000/board/create',{'kriti':"boo"}, 
    {}).then(res => {
            console.log(res)
    }).catch(function (error) {
      console.log(error);
    });
  }
}

export default App;
