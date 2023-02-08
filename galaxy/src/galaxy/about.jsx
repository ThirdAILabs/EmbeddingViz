import React from 'react';
export default require('maco').template(about, React);
import Logo from './logo.jsx'

function about() {
  return (
  <div  className='about label'>
      <div><a href="http://thirdai.com/" target='_blank'> <Logo/> </a> </div>
      <div><a className='reset-color'
        target='_blank'
          href="http://thirdai.com/contact">contact</a></div>
  </div>
  );
}
