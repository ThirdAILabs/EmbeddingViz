import React from "react";
import Destination from './destination.jsx';
import Logo from './galaxy/logo.jsx';

export default class WelcomePage extends React.Component {
  render() {
    return (
      <div className='container'>
        <Logo />

        <h1>Galaxy</h1>

        <p>Browse neighbourhood for embeddings coming out of the thirdai library.</p>

        <div className='media-list'>
          <Destination description='Amazon product catalog (kaggle), cold-start model'
            href='#/galaxy/data?l=1&v=v1'
            media='bower_fly_first.png'
            name='Amazon catalog' />

        </div>
      </div>
    );
  }
}
