import React from 'react'

import NavBar from '../components/NavBar'

export default function Layout(props) {
  return (
    <div>
      <NavBar />
      {props.children}
    </div>
  )
}
