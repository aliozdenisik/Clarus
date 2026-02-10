"use client"

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

const SQRT_5000 = Math.sqrt(5000);

const testimonials = [
  {
    tempId: 0,
    testimonial: "Finally, a tool that understands theological concepts. I searched for 'divine mercy' and got relevant verses from both Quran and Bible.",
    by: "Dr. Sarah, Religious Studies Professor",
    imgSrc: "https://i.pravatar.cc/150?img=1"
  },
  {
    tempId: 1,
    testimonial: "The multi-agent comparison changed how I prepare sermons. Seeing perspectives side-by-side is invaluable.",
    by: "Pastor Michael, Interfaith Minister",
    imgSrc: "https://i.pravatar.cc/150?img=2"
  },
  {
    tempId: 2,
    testimonial: "I've been studying comparative religion for 20 years. Clarus found connections I'd never noticed before.",
    by: "Prof. Ahmed, Comparative Theology",
    imgSrc: "https://i.pravatar.cc/150?img=3"
  },
  {
    tempId: 3,
    testimonial: "The citation traceability is exactly what academic research demands. Every insight backed by exact verses.",
    by: "Dr. Rebecca, Seminary Director",
    imgSrc: "https://i.pravatar.cc/150?img=4"
  },
  {
    tempId: 4,
    testimonial: "Searched 43,000+ verses in seconds. What used to take hours of concordance work now takes moments.",
    by: "Rev. David, Bible Scholar",
    imgSrc: "https://i.pravatar.cc/150?img=5"
  },
  {
    tempId: 5,
    testimonial: "The AI actually understands Arabic theological terms. It found relevant ayahs even when I described concepts loosely.",
    by: "Imam Yusuf, Islamic Center Director",
    imgSrc: "https://i.pravatar.cc/150?img=6"
  },
  {
    tempId: 6,
    testimonial: "My interfaith dialogue group uses Clarus weekly. It's become essential for our comparative discussions.",
    by: "Sister Maria, Ecumenical Council",
    imgSrc: "https://i.pravatar.cc/150?img=7"
  },
  {
    tempId: 7,
    testimonial: "The 5-agent synthesis produces essays I'd expect from a graduate student. Remarkable depth of analysis.",
    by: "Dr. Jonathan, Theology Department Chair",
    imgSrc: "https://i.pravatar.cc/150?img=8"
  },
  {
    tempId: 8,
    testimonial: "Finally found what I was looking for in the Apocrypha. Other tools completely ignore these texts.",
    by: "Fr. Anthony, Orthodox Priest",
    imgSrc: "https://i.pravatar.cc/150?img=9"
  },
  {
    tempId: 9,
    testimonial: "The semantic search is brilliant. I typed 'patience during suffering' and got exactly the verses I needed.",
    by: "Chaplain Grace, Hospital Ministry",
    imgSrc: "https://i.pravatar.cc/150?img=10"
  },
  {
    tempId: 10,
    testimonial: "I teach world religions to undergraduates. Clarus has become my go-to demonstration tool.",
    by: "Prof. Chen, World Religions",
    imgSrc: "https://i.pravatar.cc/150?img=11"
  },
  {
    tempId: 11,
    testimonial: "The Old Testament agent found connections to New Testament passages I'd never considered.",
    by: "Rabbi Daniel, Biblical Studies",
    imgSrc: "https://i.pravatar.cc/150?img=12"
  },
  {
    tempId: 12,
    testimonial: "Every youth group leader needs this. Makes scripture study engaging and cross-referenced.",
    by: "Jessica, Youth Ministry Director",
    imgSrc: "https://i.pravatar.cc/150?img=13"
  },
  {
    tempId: 13,
    testimonial: "The accuracy is remarkable. Tested it with obscure Quranic references and it nailed every one.",
    by: "Dr. Fatima, Quranic Studies",
    imgSrc: "https://i.pravatar.cc/150?img=14"
  },
  {
    tempId: 14,
    testimonial: "Writing my dissertation on Abrahamic traditions. Clarus cut my research time in half.",
    by: "Marcus, PhD Candidate",
    imgSrc: "https://i.pravatar.cc/150?img=15"
  },
  {
    tempId: 15,
    testimonial: "The parallel search across all collections simultaneously is a game-changer for comparative work.",
    by: "Dr. Leah, Religious Anthropologist",
    imgSrc: "https://i.pravatar.cc/150?img=16"
  },
  {
    tempId: 16,
    testimonial: "Used it to prepare an interfaith wedding ceremony. Found beautiful complementary passages instantly.",
    by: "Rev. Thomas, Wedding Officiant",
    imgSrc: "https://i.pravatar.cc/150?img=17"
  },
  {
    tempId: 17,
    testimonial: "The synthesis agent writes better comparative essays than most of my graduate students.",
    by: "Prof. Miriam, Divinity School",
    imgSrc: "https://i.pravatar.cc/150?img=18"
  },
  {
    tempId: 18,
    testimonial: "Simple interface, profound results. Exactly what theological research needed.",
    by: "Dr. Paul, Systematic Theology",
    imgSrc: "https://i.pravatar.cc/150?img=19"
  },
  {
    tempId: 19,
    testimonial: "From casual scripture reading to deep research, Clarus serves every level of inquiry.",
    by: "Hannah, Spiritual Director",
    imgSrc: "https://i.pravatar.cc/150?img=20"
  }
];

interface TestimonialCardProps {
  position: number;
  testimonial: typeof testimonials[0];
  handleMove: (steps: number) => void;
  cardSize: number;
}

const TestimonialCard: React.FC<TestimonialCardProps> = ({ 
  position, 
  testimonial, 
  handleMove, 
  cardSize 
}) => {
  const isCenter = position === 0;

  return (
    <div
      onClick={() => handleMove(position)}
      className={cn(
        "absolute left-1/2 top-1/2 cursor-pointer border-2 p-8 transition-all duration-500 ease-in-out",
        isCenter 
          ? "z-10 bg-primary text-primary-foreground border-primary" 
          : "z-0 bg-card text-card-foreground border-border hover:border-primary/50"
      )}
      style={{
        width: cardSize,
        height: cardSize,
        clipPath: `polygon(50px 0%, calc(100% - 50px) 0%, 100% 50px, 100% 100%, calc(100% - 50px) 100%, 50px 100%, 0 100%, 0 0)`,
        transform: `
          translate(-50%, -50%) 
          translateX(${(cardSize / 1.5) * position}px)
          translateY(${isCenter ? -65 : position % 2 ? 15 : -15}px)
          rotate(${isCenter ? 0 : position % 2 ? 2.5 : -2.5}deg)
        `,
        boxShadow: isCenter ? "0px 8px 0px 4px hsl(var(--border))" : "0px 0px 0px 0px transparent"
      }}
    >
      <span
        className="absolute block origin-top-right rotate-45 bg-border"
        style={{
          right: -2,
          top: 48,
          width: SQRT_5000,
          height: 2
        }}
      />
      <Image
        src={testimonial.imgSrc}
        alt={`${testimonial.by.split(',')[0]}`}
        width={48}
        height={56}
        className="mb-4 h-14 w-12 bg-muted object-cover object-top"
        style={{
          boxShadow: "3px 3px 0px hsl(var(--background))"
        }}
      />
      <h3 className={cn(
        "text-base sm:text-xl font-medium",
        isCenter ? "text-primary-foreground" : "text-foreground"
      )}>
        &ldquo;{testimonial.testimonial}&rdquo;
      </h3>
      <p className={cn(
        "absolute bottom-8 left-8 right-8 mt-2 text-sm italic",
        isCenter ? "text-primary-foreground/80" : "text-muted-foreground"
      )}>
        - {testimonial.by}
      </p>
    </div>
  );
};

export const StaggerTestimonials: React.FC = () => {
  const [cardSize, setCardSize] = useState(365);
  const [testimonialsList, setTestimonialsList] = useState(testimonials);

  const handleMove = (steps: number) => {
    const newList = [...testimonialsList];
    if (steps > 0) {
      for (let i = steps; i > 0; i--) {
        const item = newList.shift();
        if (!item) return;
        newList.push({ ...item, tempId: Math.random() });
      }
    } else {
      for (let i = steps; i < 0; i++) {
        const item = newList.pop();
        if (!item) return;
        newList.unshift({ ...item, tempId: Math.random() });
      }
    }
    setTestimonialsList(newList);
  };

  useEffect(() => {
    const updateSize = () => {
      const { matches } = window.matchMedia("(min-width: 640px)");
      setCardSize(matches ? 365 : 290);
    };

    updateSize();
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, []);

  return (
    <div
      className="relative w-full overflow-hidden bg-muted/30"
      style={{ height: 600 }}
    >
      {testimonialsList.map((testimonial, index) => {
        const position = testimonialsList.length % 2
          ? index - (testimonialsList.length + 1) / 2
          : index - testimonialsList.length / 2;
        return (
          <TestimonialCard
            key={testimonial.tempId}
            testimonial={testimonial}
            handleMove={handleMove}
            position={position}
            cardSize={cardSize}
          />
        );
      })}
      <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-2">
        <button
          onClick={() => handleMove(-1)}
          className={cn(
            "flex h-14 w-14 items-center justify-center text-2xl transition-colors",
            "bg-background border-2 border-border hover:bg-primary hover:text-primary-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          )}
          aria-label="Previous testimonial"
        >
          <ChevronLeft />
        </button>
        <button
          onClick={() => handleMove(1)}
          className={cn(
            "flex h-14 w-14 items-center justify-center text-2xl transition-colors",
            "bg-background border-2 border-border hover:bg-primary hover:text-primary-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          )}
          aria-label="Next testimonial"
        >
          <ChevronRight />
        </button>
      </div>
    </div>
  );
};
