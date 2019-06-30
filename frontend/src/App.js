import React from 'react';
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom'

import 'bulma/css/bulma.css'

import Home from './pages/Home'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import NotFound from './pages/NotFound'
import ProtectedRoute from './hoc/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Switch>
        <Route exact path="/login" component={SignIn} />
        <Route exact path="/signup" component={SignUp} />
        <ProtectedRoute exact path="/logout" render={props => <Redirect to="/login" />} />
        <ProtectedRoute path="/bookmarks" component={Home} />
        <ProtectedRoute exact path="/feeds" component={Home} />
        <ProtectedRoute exact path="/feeds/:feedUniqueName" component={Home} />
        <ProtectedRoute exact path="/feeds/:feedUniqueName/:slug" component={Home} />
        <ProtectedRoute exact path="/" component={Home} />
        <Route path="/" component={NotFound} />
      </Switch>
    </BrowserRouter>
  );
}

export default App;
