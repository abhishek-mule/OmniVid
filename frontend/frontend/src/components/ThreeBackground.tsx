'use client';

import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function ThreeBackground() {
  const mountRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef<number>();
  const startTimeRef = useRef<number>(Date.now());

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true
    });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    mountRef.current.appendChild(renderer.domElement);

    // Shader uniforms
    const uniforms = {
      u_time: { value: 0 },
      u_resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
      u_mouse: { value: new THREE.Vector2(0, 0) },
      u_noise: { value: null as THREE.Texture | null }
    };

    // Load noise texture
    const textureLoader = new THREE.TextureLoader();
    textureLoader.setCrossOrigin('anonymous');
    textureLoader.load(
      'https://s3-us-west-2.amazonaws.com/s.cdpn.io/982762/noise.png',
      (texture) => {
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.minFilter = THREE.LinearFilter;
        uniforms.u_noise.value = texture;
      }
    );

    // Shader material
    const material = new THREE.ShaderMaterial({
      uniforms,
      vertexShader: `
        void main() {
          gl_Position = vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform vec2 u_resolution;
        uniform vec2 u_mouse;
        uniform float u_time;
        uniform sampler2D u_noise;

        vec3 hash33(vec3 p){ 
          return texture2D(u_noise, p.xy * p.z * 256.).rgb;
        }

        float pn(in vec3 p) {
          vec3 i = floor(p); p -= i; p *= p*(3. - 2.*p);
          p.xy = texture2D(u_noise, (p.xy + i.xy + vec2(37, 17)*i.z + .5)/256., -100.).yx;
          return mix(p.x, p.y, p.z);
        }

        float trigNoise3D(in vec3 p) {
          float res = 0., sum = 0.;
          float n = pn(p*8. + u_time*.5);
          vec3 t = sin(p.yzx*3.14159265 + cos(p.zxy*3.14159265+1.57/2.))*0.5 + 0.5;
          p = p*1.5 + (t - 1.5);
          res += (dot(t, vec3(0.333)));
          t = sin(p.yzx*3.14159265 + cos(p.zxy*3.14159265+1.57/2.))*0.5 + 0.5;
          res += (dot(t, vec3(0.333)))*0.7071;    
          return ((res/1.7071))*0.85 + n*0.15;
        }

        float world(vec3 p) {
          float n = trigNoise3D(p*0.2);
          float t = sin(u_time*.0001)*.5+.5;
          float c = cos(p.z*.2*t+n);
          float s = sin(p.z*.05+n*.5);
          p.xy *= mat2(c, -s, s, c);
          p -= n*1.5;
          p.y = mod(p.y, 4.0 + p.y * .5) - 2. - p.y * .25;
          return abs(p.y) - .1;
        }

        void main() {
          vec2 aspect = vec2(u_resolution.x/u_resolution.y, 1.0);
          vec2 uv = (2.0*gl_FragCoord.xy/u_resolution.xy - 1.0)*aspect;
          float modtime = u_time * .1;
          
          vec3 lookAt = vec3(sin(modtime)*2. + u_mouse.x*2., u_mouse.y*2., 2. + u_time*2.);
          vec3 camera_position = vec3(sin(modtime)*3., 0, u_time*2.);
          
          vec3 forward = normalize(lookAt-camera_position);
          vec3 right = normalize(vec3(forward.z, 0., -forward.x));
          vec3 up = normalize(cross(forward,right));

          float FOV = 1.1;
          vec3 ro = camera_position; 
          vec3 rd = normalize(forward + FOV*uv.x*right + FOV*uv.y*up);

          vec3 lp = vec3(-3, 2, -1.5);
          lp += ro;
          ro.x += u_mouse.x;
          ro.y += u_mouse.y;

          float local_density = 0.;
          float density = 0.;
          float weighting = 0.;
          float dist = 1.;
          float travelled = 0.;
          const float distanceThreshold = .1;
          vec3 col = vec3(0);
          vec3 sp;
          vec3 sn = normalize(-rd);

          for (int i=0; i<64; i++) {
            if((density>1.) || travelled>80.) break;
            sp = ro + rd*travelled;
            dist = world(sp);
            if(dist < .2) dist = .35;
            local_density = (distanceThreshold - dist)*step(dist, distanceThreshold);
            weighting = (1. - density)*local_density;
            density += weighting*(1.-distanceThreshold)*1./dist;
            vec3 ld = lp-sp;
            float lDist = max(length(ld), .001);
            ld/=lDist;
            float atten = 1./(1. + lDist*.125 + lDist*lDist*.55);
            float diff = max(dot(sn, ld), 0.);
            float spec = pow(max(dot(reflect(-ld, sn), -rd), 0.), 4.);
            col += weighting*atten*1.25;
            travelled += max(dist*.4, .02);
          }

          col = max(col, 0.);
          col = mix(vec3(.0, .1, .3), vec3(2.), col);
          col = mix(col, vec3(2.), travelled*.01);
          col = mix(col.zyx, col, dot(rd, col.xyz)+.5*travelled*.05);
          col *= col*col*col*1.15;

          gl_FragColor = vec4(sqrt(col), 1.0);
        }
      `
    });

    // Geometry
    const geometry = new THREE.PlaneGeometry(2, 2);
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // Handle mouse movement
    const handleMouseMove = (e: MouseEvent) => {
      const ratio = window.innerHeight / window.innerWidth;
      uniforms.u_mouse.value.x = (e.clientX - window.innerWidth / 2) / window.innerWidth / ratio;
      uniforms.u_mouse.value.y = (e.clientY - window.innerHeight / 2) / (window.innerHeight * -1);
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Handle resize
    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      renderer.setSize(width, height);
      uniforms.u_resolution.value.set(width, height);
      
      if (width > height) {
        camera.left = -width / height;
        camera.right = width / height;
        camera.top = 1;
        camera.bottom = -1;
      } else {
        camera.left = -1;
        camera.right = 1;
        camera.top = height / width;
        camera.bottom = -height / width;
      }
      
      camera.updateProjectionMatrix();
    };
    window.addEventListener('resize', handleResize);
    handleResize();

    // Animation loop
    const animate = () => {
      const currentTime = Date.now();
      const elapsedTime = (currentTime - startTimeRef.current) * 0.001; // Convert to seconds
      uniforms.u_time.value = elapsedTime * 0.5; // Slow down the animation
      
      renderer.render(scene, camera);
      frameRef.current = requestAnimationFrame(animate);
    };
    frameRef.current = requestAnimationFrame(animate);

    // Cleanup
    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      if (mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: -1,
        opacity: 0.5 // Adjust opacity as needed
      }}
    />
  );
}
