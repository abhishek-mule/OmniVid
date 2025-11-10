'use client';

import { useRef, useState } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay, Parallax, EffectCreative, Mousewheel } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import 'swiper/css/parallax';
import 'swiper/css/effect-creative';
import { motion } from 'framer-motion';
import { ArrowLongRightIcon, ArrowLongLeftIcon } from '@heroicons/react/24/outline';

const slides = [
  {
    id: 1,
    image: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1920&q=80',
    tag: 'AI POWERED',
    title: 'CREATE',
    description: 'Transform your ideas into stunning videos with cutting-edge AI technology. Experience the future of content creation.',
    buttonText: 'Start Creating',
    gradient: 'from-purple-600/20 to-blue-600/20'
  },
  {
    id: 2,
    image: 'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=1920&q=80',
    tag: 'INNOVATION',
    title: 'INSPIRE',
    description: 'Unleash your creativity with intuitive tools designed for modern storytellers. Make every frame count.',
    buttonText: 'Explore Features',
    gradient: 'from-pink-600/20 to-orange-600/20'
  },
  {
    id: 3,
    image: 'https://images.unsplash.com/photo-1536240478700-b869070f9279?w=1920&q=80',
    tag: 'EXCELLENCE',
    title: 'DELIVER',
    description: 'Professional-grade results in minutes, not hours. Elevate your content to new heights effortlessly.',
    buttonText: 'Get Started',
    gradient: 'from-cyan-600/20 to-teal-600/20'
  }
];

export default function CreativeSlider() {
  const swiperRef = useRef<any>(null);
  const paginationRef = useRef<HTMLDivElement>(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isVisible] = useState(true);

  return (
    <section 
      className="creative-fullpage--slider relative"
    >
      <div className="banner-horizental">
        <Swiper
          ref={swiperRef}
          modules={[Navigation, Pagination, Autoplay, Parallax, EffectCreative, Mousewheel]}
          spaceBetween={0}
          slidesPerView={1}
          speed={1200}
          loop={true}
          mousewheel={{
            forceToAxis: true,
            sensitivity: 1,
            releaseOnEdges: true,
          }}
          autoplay={{
            delay: 8000,
            disableOnInteraction: false,
            pauseOnMouseEnter: true,
          }}
          parallax={true}
          effect="creative"
          creativeEffect={{
            prev: {
              shadow: true,
              translate: ["-20%", 0, -1],
              opacity: 0.5,
            },
            next: {
              translate: ["100%", 0, 0],
            },
          }}
          navigation={{
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
          }}
          pagination={{
            el: '.swiper-pagination',
            type: 'progressbar',
          }}
          onSwiper={(swiper) => {
            if (paginationRef.current) {
              const progress = (swiper.realIndex + 1) / slides.length * 100;
              paginationRef.current.style.width = `${progress}%`;
            }
          }}
          onSlideChange={(swiper) => {
            setCurrentSlide(swiper.realIndex);
            if (paginationRef.current) {
              const progress = (swiper.realIndex + 1) / slides.length * 100;
              paginationRef.current.style.width = `${progress}%`;
            }
          }}
          className="swiper-container-h w-full h-screen"
        >
          {slides.map((slide, index) => (
            <SwiperSlide key={slide.id} className="relative overflow-hidden">
              <motion.div 
                className="slider-inner relative"
                initial={{ scale: 1.1 }}
                animate={{ scale: currentSlide === index ? 1 : 1.1 }}
                transition={{ duration: 1.2, ease: "easeOut" }}
              >
                {/* Background Image with Parallax */}
                <motion.div
                  className="absolute inset-0"
                  data-swiper-parallax="-300"
                >
                  <img 
                    src={slide.image} 
                    alt={slide.title} 
                    className="w-full h-screen object-cover"
                  />
                </motion.div>

                {/* Gradient Overlay */}
                <div className={`absolute inset-0 bg-gradient-to-br ${slide.gradient}`}></div>
                <div className="absolute inset-0 bg-black/40"></div>

                {/* Animated Content */}
                <div 
                  className="swiper-content absolute top-1/2 left-12 md:left-20 transform -translate-y-1/2 z-10 text-white max-w-3xl"
                  data-swiper-parallax="500"
                >
                  {/* Tag with stagger animation */}
                  {slide.tag && (
                    <motion.div
                      initial={{ opacity: 0, x: -50 }}
                      animate={{ opacity: currentSlide === index ? 1 : 0, x: currentSlide === index ? 0 : -50 }}
                      transition={{ duration: 0.6, delay: 0.2 }}
                      className="mb-6"
                    >
                      <span className="inline-block px-4 py-2 text-sm font-bold tracking-wider bg-white/10 backdrop-blur-md rounded-full border border-white/20">
                        {slide.tag}
                      </span>
                    </motion.div>
                  )}

                  {/* Title with split animation */}
                  <motion.div 
                    className="title-area mb-8 overflow-hidden"
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: currentSlide === index ? 1 : 0, y: currentSlide === index ? 0 : 50 }}
                    transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
                  >
                    <h2 className="text-6xl md:text-8xl lg:text-9xl font-black mb-6 leading-none tracking-tight">
                      <span className="inline-block bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/80">
                        {slide.title}
                      </span>
                    </h2>
                  </motion.div>

                  {/* Description */}
                  <motion.p 
                    className="text-lg md:text-xl mb-10 text-white/90 leading-relaxed max-w-2xl"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: currentSlide === index ? 1 : 0, y: currentSlide === index ? 0 : 30 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                  >
                    {slide.description}
                  </motion.p>

                  {/* CTA Button */}
                  <motion.div 
                    className="creative-btn--wrap"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: currentSlide === index ? 1 : 0, y: currentSlide === index ? 0 : 20 }}
                    transition={{ duration: 0.8, delay: 0.8 }}
                  >
                    <a 
                      href="#features" 
                      className="creative-slide--btn inline-flex items-center text-white text-lg font-semibold group relative overflow-hidden"
                    >
                      <span className="relative w-14 h-14 flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300">
                        <span className="absolute inset-0 rounded-full bg-white/20 backdrop-blur-sm group-hover:bg-white group-hover:scale-125 transition-all duration-500"></span>
                        <span className="absolute inset-0 rounded-full bg-white/10 animate-ping"></span>
                        <ArrowLongRightIcon className="w-7 h-7 relative z-10 transform group-hover:translate-x-1 group-hover:text-black transition-all duration-300" />
                      </span>
                      <span className="relative">
                        <span className="relative z-10">{slide.buttonText}</span>
                        <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-500"></span>
                      </span>
                    </a>
                  </motion.div>
                </div>

                {/* Decorative Elements */}
                <motion.div
                  className="absolute top-20 right-20 w-32 h-32 border-2 border-white/20 rounded-full"
                  animate={{
                    scale: [1, 1.2, 1],
                    rotate: [0, 180, 360],
                  }}
                  transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                />
                <motion.div
                  className="absolute bottom-32 right-40 w-20 h-20 border-2 border-white/10 rounded-full"
                  animate={{
                    scale: [1, 1.3, 1],
                    rotate: [360, 180, 0],
                  }}
                  transition={{
                    duration: 15,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                />
              </motion.div>
            </SwiperSlide>
          ))}
          
          {/* Enhanced Navigation Buttons */}
          <motion.div 
            className="swiper-button-wrapper creative-button--wrapper absolute bottom-12 left-0 right-0 z-20 flex justify-between px-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: isVisible ? 1 : 0, y: isVisible ? 0 : 20 }}
            transition={{ duration: 0.8, delay: 1 }}
          >
            <motion.button 
              className="swiper-button-prev w-16 h-16 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center hover:bg-white/30 hover:scale-110 transition-all duration-300 border border-white/20"
              aria-label="Previous slide"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <ArrowLongLeftIcon className="w-8 h-8 text-white" />
            </motion.button>
            <motion.button 
              className="swiper-button-next w-16 h-16 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center hover:bg-white/30 hover:scale-110 transition-all duration-300 border border-white/20"
              aria-label="Next slide"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <ArrowLongRightIcon className="w-8 h-8 text-white" />
            </motion.button>
          </motion.div>
          
          {/* Enhanced Custom Pagination */}
          <motion.div 
            className="slider-pagination-area absolute bottom-12 left-1/2 transform -translate-x-1/2 flex items-center z-20 bg-black/20 backdrop-blur-md px-6 py-3 rounded-full border border-white/10"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: isVisible ? 1 : 0, y: isVisible ? 0 : 20 }}
            transition={{ duration: 0.8, delay: 1.2 }}
          >
            <span className="text-white text-lg font-bold mr-4">
              {String(currentSlide + 1).padStart(2, '0')}
            </span>
            <div className="w-40 h-1 bg-white/20 relative overflow-hidden rounded-full">
              <motion.div 
                ref={paginationRef}
                className="absolute left-0 top-0 h-full bg-gradient-to-r from-white via-white/90 to-white rounded-full"
                style={{ width: `${100 / slides.length}%` }}
                animate={{
                  boxShadow: [
                    "0 0 10px rgba(255,255,255,0.5)",
                    "0 0 20px rgba(255,255,255,0.8)",
                    "0 0 10px rgba(255,255,255,0.5)"
                  ]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            </div>
            <span className="text-white text-lg font-bold ml-4">
              {String(slides.length).padStart(2, '0')}
            </span>
          </motion.div>
        </Swiper>
      </div>
      
      {/* Scroll Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-30 hidden md:flex flex-col items-center gap-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: isVisible ? 1 : 0 }}
        transition={{ duration: 1, delay: 1.5 }}
      >
        <span className="text-white/60 text-xs uppercase tracking-wider">Scroll</span>
        <motion.div
          className="w-6 h-10 border-2 border-white/30 rounded-full p-1"
          animate={{
            borderColor: ["rgba(255,255,255,0.3)", "rgba(255,255,255,0.6)", "rgba(255,255,255,0.3)"]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <motion.div
            className="w-1 h-2 bg-white rounded-full mx-auto"
            animate={{
              y: [0, 12, 0]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </motion.div>
      </motion.div>

    </section>
  );
}