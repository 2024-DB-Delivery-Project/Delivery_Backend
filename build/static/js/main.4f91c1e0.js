/*! For license information please see main.4f91c1e0.js.LICENSE.txt */
  0% {
    transform: scale(0);
    opacity: 0.1;
  }

  100% {
    transform: scale(1);
    opacity: 0.3;
  }
`,ha=vs`
  0% {
    opacity: 1;
  }

  100% {
    opacity: 0;
  }
`,za=vs`
  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(0.92);
  }

  100% {
    transform: scale(1);
  }
`,La=Sr("span",{name:"MuiTouchRipple",slot:"Root"})({overflow:"hidden",pointerEvents:"none",position:"absolute",zIndex:0,top:0,right:0,bottom:0,left:0,borderRadius:"inherit"}),Ma=Sr(fa,{name:"MuiTouchRipple",slot:"Ripple"})`
  opacity: 0;
  position: absolute;

  &.${ma.rippleVisible} {
    opacity: 0.3;
    transform: scale(1);
    animation-name: ${pa};
    animation-duration: ${550}ms;
    animation-timing-function: ${e=>{let{theme:c}=e;return c.transitions.easing.easeInOut}};
  }

  &.${ma.ripplePulsate} {
    animation-duration: ${e=>{let{theme:c}=e;return c.transitions.duration.shorter}}ms;
  }

  & .${ma.child} {
    opacity: 1;
    display: block;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background-color: currentColor;
  }

  & .${ma.childLeaving} {
    opacity: 0;
    animation-name: ${ha};
    animation-duration: ${550}ms;
    animation-timing-function: ${e=>{let{theme:c}=e;return c.transitions.easing.easeInOut}};
  }

  & .${ma.childPulsate} {
    position: absolute;
    /* @noflip */
    left: 0px;
    top: 0;
    animation-name: ${za};
    animation-duration: 2500ms;
    animation-timing-function: ${e=>{let{theme:c}=e;return c.transitions.easing.easeInOut}};
    animation-iteration-count: infinite;
    animation-delay: 200ms;
  }
//# sourceMappingURL=main.4f91c1e0.js.map