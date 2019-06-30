import React from 'react'
import {Route, Redirect} from 'react-router-dom'

export default function PrivateRoute(props) {
  return (
    localStorage.getItem('token')
    ? <Route {...props} /> : <Redirect to="/login" />
  )
}
