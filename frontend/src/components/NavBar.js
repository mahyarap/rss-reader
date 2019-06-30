import React from 'react'
import { Link, withRouter } from "react-router-dom";

import axios from '../API'

class NavBar extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      subscription: '',
      errors: []
    }

    this.handleLogout = this.handleLogout.bind(this)
    this.handleSubscribe = this.handleSubscribe.bind(this)
    this.handleFieldChange = this.handleFieldChange.bind(this)
  }

  handleLogout() {
    localStorage.removeItem('token')
  }

  async handleSubscribe(event) {
    if (!this.state.subscription) {
      return
    }

    try {
      await axios.post('/feeds/', {url: this.state.subscription})
      this.setState({
        subscription: '',
        isSuccess: true,
        errors: []
      })
      window.location.href = '/feeds'
      // this.props.history.push('/')
    } catch (excep) {
      const errors = []
      for (const key in excep.response.data) {
        excep.response.data[key].forEach(e => errors.push(e)) 
      }
      this.setState({
        errors: errors,
        subscription: ''
      })
    }
  }

  handleFieldChange(event) {
    this.setState({
      [event.target.name]: event.target.value
    })
  }

  render() {
    return (
      <nav className="navbar is-primary" role="navigation" aria-label="main navigation">
        <div className="navbar-brand">
          <a className="navbar-item" href="/">
            <img
              src="https://1h19u2763213rkq602x0udv1-wpengine.netdna-ssl.com/wp-content/uploads/2017/02/New-Logo-White-Mini.png"
              width="112"
              height="28"
              alt=""
            />
          </a>

          <button
            className="navbar-burger burger"
            aria-label="menu"
            aria-expanded="false"
            data-target="navbarBasicExample"
          >
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </button>
        </div>

        <div className="navbar-menu">
          <div className="navbar-start">
            <div className="navbar-item">
              <div className="field has-addons">
                <div className="control">
                  <input
                    name="subscription"
                    type="url"
                    className={this.state.errors.length > 0 ? 'input is-danger' : 'input'}
                    placeholder={this.state.errors[0] || 'Enter URL here'}
                    onChange={this.handleFieldChange}
                    value={this.state.subscription}
                  />
                  </div>
                  <div className="control">
                    <button
                      className="button is-info"
                      onClick={this.handleSubscribe}
                    >
                      Subscribe
                    </button>
                  </div>
                </div>
              </div>
            </div>

          <div className="navbar-end">
            <div className="navbar-item">
              <div className="buttons">
                {
                  localStorage.getItem('token')
                    ?
                    <Link
                      to="/logout"
                      onClick={this.handleLogout}
                      className="button is-light"
                    >
                      Log out
                    </Link>
                    :
                    <React.Fragment>
                      <Link to="/signup" className="button is-primary">
                        <strong>Sign up</strong>
                      </Link>
                      <Link to="/login" className="button is-light">
                        Log in
                      </Link>
                    </React.Fragment>
                }
              </div>
            </div>
          </div>
        </div>
      </nav>
    )
  }
}

export default withRouter(NavBar)
