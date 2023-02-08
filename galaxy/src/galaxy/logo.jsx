import React from 'react';
import logoImage from '../images/ThirdAI_logo.svg';
export default require('maco').template(logo, React);

function logo() {
  return (
    <img src={logoImage} width="200"/>
  );
}
