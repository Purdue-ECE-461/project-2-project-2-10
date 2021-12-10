import React from 'react'
import { Link } from 'react-router-dom'

import '../../App.css'
import BackgroundImage from '../../assets/images/back2.png'

export default function LandingPage() {
    return (
        <header style={ HeaderStyle }>
            <h1 className="main-title">ECE 461</h1>
            <p className="main-para">Dev Rana, John Bensen, Richard Rhee</p>
            <div className="buttons">
                <Link to="/login">
                    <button className="primary-button">log in</button>
                </Link>
                <Link to="/register">
                    <button className="primary-button" id="reg_btn"><span>register </span></button>
                </Link>
            </div>
        </header>
    )
}

const HeaderStyle = {
    // width: "800px",
    // height: "550px",
    height: "100vh",
    background: `url(${BackgroundImage})`,
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    BackgroundImage: "fill",
    margin: "0 auto",
    postion: "relative",
    // borderRadius: "19px",
    backgroundcolor: "#fff",
    boxshadow: "0 0 2px rgba(15, 15, 15, 0.28)"
}