import React from 'react'

import Layout from '../layout/Bare'

export default function NotFound(props) {
  return (
    <Layout>
      <section className="hero is-light" style={{marginTop: 100}}>
        <div className="hero-body">
          <div className="container">
            <h1 className="title has-text-centered">
              404 Not Found
            </h1>
            <h2 className="subtitle has-text-centered">
              The page you're looking for is not here :-/
            </h2>
          </div>
        </div>
    </section>
    </Layout>
  )
}
