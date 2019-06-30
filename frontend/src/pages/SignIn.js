import React from 'react'

import { Link } from "react-router-dom";

import axios from '../API'
import Layout from '../layout/Bare'

export default class SignIn extends React.Component {
  constructor(props) {
    super(props)

    let msg = {}
    if (this.props.location.state && this.props.location.state.accountCreated) {
      msg = {
        text: 'Account successfully created. You may log in now!',
        type: 'success'
      }
    }

    this.state = {
      username: '',
      password: '',
      msg: msg
    }

    this.handleFormSubmit = this.handleFormSubmit.bind(this)
    this.handleFieldChange = this.handleFieldChange.bind(this)
  }

  handleFieldChange(event) {
    this.setState({
      [event.target.name]: event.target.value
    })
  }

  async handleFormSubmit(event) {
    event.preventDefault()
    const creds = {
      username: this.state.username,
      password: this.state.password
    }
    try {
      const resp = await axios.post('/login/', creds)
      localStorage.setItem('token', resp.data.token)
      this.setState({
        error: ''
      })
      this.props.history.replace('/')
    } catch(e) {
      this.setState({
        msg: {
          text: Object.values(e.response.data),
          type: 'danger'
        }
      })
    }
  }

  render() {
    return (
      <Layout>
        <div className="container">
          <div className="columns is-centered">
            <div className="column is-one-third">

              <div style={{marginTop: 100}}>
                {
                  this.state.msg.text
                  ?
                  <div className={'message is-small is-' + this.state.msg.type}>
                    <div className="message-body">
                      {this.state.msg.text}
                    </div>
                  </div>
                  :
                  null
                }
                <div className="box">
                  <form onSubmit={this.handleFormSubmit}>
                    <div className="field">
                      <label className="label">Username</label>
                      <div className="control">
                        <input
                          name="username"
                          className="input"
                          type="text"
                          placeholder="Enter username"
                          value={this.state.username}
                          onChange={this.handleFieldChange}
                          required
                        />
                      </div>
                    </div>

                    <div className="field">
                      <label className="label">Password</label>
                      <div className="control">
                        <input
                          name="password"
                          className="input"
                          type="password"
                          placeholder="Enter password"
                          value={this.state.password}
                          onChange={this.handleFieldChange}
                          required
                        />
                      </div>
                    </div>

                    <div className="field is-grouped is-grouped-centered">
                      <div className="control">
                        <input
                          type="submit"
                          className="button is-link"
                          value="Login"
                        />
                      </div>
                    </div>
                  </form>
                </div>
                <p className="has-text-centered">
                  Don't have an account? <Link to="/signup">Sign up</Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    )
  }
}
