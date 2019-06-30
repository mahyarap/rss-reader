import React from 'react'
import { Redirect } from "react-router-dom"

import axios from '../API'
import Layout from '../layout/Bare'

export default class SignIn extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      username: '',
      password: '',
      password_repeat: '',
      error: '',
      isSuccess: false
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
      password: this.state.password,
      password_repeat: this.state.password_repeat
    }

    if (creds.password !== creds.password_repeat) {
      this.setState({
        error: 'Passwords do not match'
      })
      return
    }

    try {
      await axios.post('/signup/', creds)
      this.setState({
        isSuccess: true
      })
    } catch(e) {
      this.setState({
        error: Object.values(e.response.data),
        isSuccess: false
      })
    }
  }

  render() {
    if (this.state.isSuccess) {
      return <Redirect to={{pathname: '/login', state: {accountCreated: true}}} />
    }

    return (
      <Layout>
        <div className="container">
          <div className="columns is-centered">
            <div className="column is-one-third">

              <div style={{marginTop: 100}}>
                {
                  this.state.error &&
                  <div className="message is-small is-danger">
                    <div className="message-body">
                      {this.state.error}
                    </div>
                  </div>
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

                    <div className="field">
                      <label className="label">Repeat password</label>
                      <div className="control">
                        <input
                          name="password_repeat"
                          className="input"
                          type="password"
                          placeholder="Repeat password"
                          value={this.state.password_repeat}
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
                          value="Sign Up"
                        />
                      </div>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    )
  }
}
