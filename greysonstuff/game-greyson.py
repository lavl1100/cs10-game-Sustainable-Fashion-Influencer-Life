"""
CLOUT.EXE — A Social Media Platform Simulator
Built with Python + Arcade 3.x
"""

import arcade
import arcade.gui
import random
import math
import time
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

SCREEN_W, SCREEN_H = 1000, 700
TITLE = "CLOUT.EXE"
BG = (10, 10, 18)

C_ACCENT  = (80, 240, 160)
C_PINK    = (255, 80, 160)
C_YELLOW  = (255, 220, 60)
C_BLUE    = (60, 180, 255)
C_RED     = (255, 80, 80)
C_DARK    = (20, 20, 32)
C_MID     = (35, 35, 55)
C_LIGHT   = (160, 160, 200)
C_WHITE   = (230, 230, 240)
C_PURPLE  = (160, 80, 255)

# ── Arcade 3.x rectangle helpers (old API used cx,cy,w,h; new uses LBWH) ────
def _lbwh(cx, cy, w, h):
    return arcade.LBWH(cx - w / 2, cy - h / 2, w, h)

def draw_rect_filled(cx, cy, w, h, color):
    arcade.draw_rect_filled(_lbwh(cx, cy, w, h), color)

def draw_rect_outline(cx, cy, w, h, color, border=1):
    arcade.draw_rect_outline(_lbwh(cx, cy, w, h), color, border)

# ── Post Types ───────────────────────────────────────────────────────────────
class PostType(Enum):
    MEME     = "meme"
    SELFIE   = "selfie"
    HOT_TAKE = "hot take"
    ESSAY    = "essay"
    VIDEO    = "video"
    THIRST   = "thirst trap"
    RANT     = "unhinged rant"

POST_CONFIG = {
    PostType.MEME:     {"emoji":"😂","viral":0.35,"ratio_risk":0.05,"unlock":0,    "color":C_YELLOW},
    PostType.SELFIE:   {"emoji":"🤳","viral":0.20,"ratio_risk":0.03,"unlock":0,    "color":C_PINK},
    PostType.HOT_TAKE: {"emoji":"🔥","viral":0.40,"ratio_risk":0.30,"unlock":100,  "color":C_RED},
    PostType.ESSAY:    {"emoji":"📝","viral":0.15,"ratio_risk":0.02,"unlock":200,  "color":C_BLUE},
    PostType.VIDEO:    {"emoji":"🎬","viral":0.50,"ratio_risk":0.10,"unlock":500,  "color":C_PURPLE},
    PostType.THIRST:   {"emoji":"💅","viral":0.60,"ratio_risk":0.20,"unlock":1000, "color":C_PINK},
    PostType.RANT:     {"emoji":"😤","viral":0.55,"ratio_risk":0.50,"unlock":2000, "color":C_RED},
}

RANDOM_EVENTS = [
    {"name":"Algorithm Boost","prob":0.08,"effect":3.0, "color":C_ACCENT,"msg":"🚀 The algorithm loves you!"},
    {"name":"Shadowban",      "prob":0.05,"effect":0.1, "color":C_RED,   "msg":"👻 You've been shadowbanned..."},
    {"name":"Celeb Repost",   "prob":0.03,"effect":10.0,"color":C_YELLOW,"msg":"⭐ A celebrity reposted you!"},
    {"name":"Bot Attack",     "prob":0.06,"effect":0.5, "color":C_PURPLE,"msg":"🤖 Bots are ratio-ing you!"},
    {"name":"Trend Surfing",  "prob":0.10,"effect":2.0, "color":C_BLUE,  "msg":"📈 You caught a trending wave!"},
    {"name":"Platform Outage","prob":0.04,"effect":0.0, "color":C_MID,   "msg":"💀 Platform is down. No reach."},
]

QUALITY_LABELS = ["bad","mid","decent","good","banger"]

@dataclass
class Particle:
    x:float; y:float; vx:float; vy:float
    life:float; max_life:float; color:tuple; size:float; text:str=""

@dataclass
class PostRecord:
    post_type:PostType; quality:int; likes:int; shares:int
    followers_gained:int; event:str; timestamp:float

@dataclass
class FeedItem:
    y:float; record:PostRecord; alpha:float=255.0; slide_x:float=400.0


class SocialMediaGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_W, SCREEN_H, TITLE, resizable=False)
        self.background_color = arcade.types.Color(*BG)
        self.setup()

    def setup(self):
        self.followers=0.0; self.total_posts=0; self.total_likes=0
        self.energy=100.0; self.energy_regen=8.0; self.streak=0
        self.best_post=None; self.particles=[]; self.feed_items=[]
        self.notifications=[]; self.active_event=None; self.event_timer=0.0
        self.selected_quality=2; self.selected_type_idx=0
        self.available_types=[]; self._refresh_available()
        self.posting_anim=0.0; self.total_time=0.0
        self.milestones={
            10:"10 followers — mom found your account 😬",
            100:"100 followers — you're basically famous",
            500:"500 followers — okay this is real",
            1000:"1K followers 🎉 — four-digit crew",
            5000:"5K followers — brand deals incoming?",
            10000:"10K FOLLOWERS — verified check soon??",
            50000:"50K — you're going to be ok",
        }
        self.reached_milestones=set()

    def _refresh_available(self):
        self.available_types=[pt for pt,cfg in POST_CONFIG.items() if self.followers>=cfg["unlock"]]

    def post_content(self):
        if self.energy<20:
            self._notify("Not enough energy! Rest a bit 😴",C_RED); return
        if not self.available_types: return

        pt=self.available_types[self.selected_type_idx%len(self.available_types)]
        cfg=POST_CONFIG[pt]; quality=self.selected_quality
        self.energy=max(0,self.energy-20+quality*2)

        viral_chance=max(0.05,min(0.95,cfg["viral"]+(quality-2)*0.10+min(self.streak*0.03,0.15)))
        active_event=None
        for ev in RANDOM_EVENTS:
            if random.random()<ev["prob"]:
                active_event=ev; self.active_event=ev; self.event_timer=4.0; break

        event_mult=active_event["effect"] if active_event else 1.0
        went_viral=random.random()<viral_chance
        got_ratiod=random.random()<cfg["ratio_risk"]+(4-quality)*0.05

        base_likes=random.randint(1,max(2,int(self.followers*0.15+5)))
        if went_viral:
            likes=int(base_likes*random.uniform(5,20)*event_mult*(quality+1))
        else:
            likes=int(base_likes*event_mult*((quality+1)/3))

        if got_ratiod: likes=max(0,int(likes*random.uniform(0.1,0.5))); shares=0
        else: shares=int(likes*random.uniform(0.1,0.4))

        if got_ratiod: gained=-random.randint(1,max(1,int(self.followers*0.05)+5)); self.streak=0
        elif went_viral: gained=int(likes*random.uniform(0.2,0.6)); self.streak+=1
        else:
            gained=max(0,int(likes*random.uniform(0.05,0.15)))
            self.streak=self.streak+1 if gained>0 else max(0,self.streak-1)

        if event_mult==0.0: gained=0; likes=0; shares=0

        self.followers=max(0,self.followers+gained)
        self.total_likes+=likes; self.total_posts+=1

        rec=PostRecord(pt,quality,likes,shares,gained,
                       active_event["name"] if active_event else "normal",time.time())
        if self.best_post is None or rec.likes>self.best_post.likes: self.best_post=rec

        fi=FeedItem(y=SCREEN_H-100,record=rec)
        self.feed_items.insert(0,fi)
        if len(self.feed_items)>6: self.feed_items.pop()

        self._spawn_post_particles(pt,went_viral,got_ratiod,gained)
        if got_ratiod: self._notify(f"💀 RATIO'D! -{abs(gained)} followers",C_RED)
        elif went_viral: self._notify(f"🔥 VIRAL! +{gained:,} followers!",C_ACCENT)
        else: self._notify(f"+{gained} followers",C_LIGHT)
        if active_event: self._notify(active_event["msg"],active_event["color"])

        self._refresh_available(); self._check_milestones(); self.posting_anim=1.0

    def _check_milestones(self):
        for thresh,msg in self.milestones.items():
            if self.followers>=thresh and thresh not in self.reached_milestones:
                self.reached_milestones.add(thresh); self._notify(f"🏆 {msg}",C_YELLOW)

    def _spawn_post_particles(self,pt,viral,ratiod,gained):
        x0,y0=780,360
        color=C_RED if ratiod else(C_ACCENT if viral else POST_CONFIG[pt]["color"])
        emojis=["✨","💥","⚡","🔥","💫"] if viral else(["💀","😭","📉"] if ratiod else["👍","❤️","🔁"])
        for _ in range(30 if viral else 8):
            angle=random.uniform(0,math.tau); speed=random.uniform(50,250 if viral else 120)
            life=random.uniform(0.8,2.0)
            self.particles.append(Particle(
                x=x0+random.uniform(-20,20),y=y0+random.uniform(-20,20),
                vx=math.cos(angle)*speed,vy=math.sin(angle)*speed,
                life=life,max_life=life,color=color,
                size=random.uniform(3,8 if viral else 5),
                text=random.choice(emojis) if random.random()<0.3 else ""))

    def _notify(self,msg,color):
        self.notifications.append({"msg":msg,"color":color,"timer":3.0,"y":SCREEN_H-40})
        if len(self.notifications)>5: self.notifications.pop(0)

    def on_update(self,dt):
        self.total_time+=dt; self.energy=min(100,self.energy+self.energy_regen*dt)
        for p in self.particles[:]:
            p.x+=p.vx*dt; p.y+=p.vy*dt; p.vy-=200*dt; p.life-=dt
            if p.life<=0: self.particles.remove(p)
        for n in self.notifications[:]:
            n["timer"]-=dt; n["y"]+=20*dt
            if n["timer"]<=0: self.notifications.remove(n)
        if self.event_timer>0:
            self.event_timer-=dt
            if self.event_timer<=0: self.active_event=None
        for fi in self.feed_items:
            fi.slide_x=max(0,fi.slide_x-600*dt)
            if fi.slide_x==0:
                target_y=SCREEN_H-100-self.feed_items.index(fi)*75
                fi.y+=(target_y-fi.y)*5*dt
        if self.posting_anim>0: self.posting_anim=max(0,self.posting_anim-3*dt)

    def on_draw(self):
        self.clear()
        self._draw_bg(); self._draw_left_panel(); self._draw_right_panel()
        self._draw_feed(); self._draw_particles(); self._draw_notifications()
        if self.active_event: self._draw_event_banner()

    def _draw_bg(self):
        for x in range(0,SCREEN_W,60): arcade.draw_line(x,0,x,SCREEN_H,(20,20,35),1)
        for y in range(0,SCREEN_H,60): arcade.draw_line(0,y,SCREEN_W,y,(20,20,35),1)
        if self.posting_anim>0:
            draw_rect_filled(SCREEN_W//2,SCREEN_H//2,SCREEN_W,SCREEN_H,(*C_ACCENT,int(self.posting_anim*40)))

    def _draw_left_panel(self):
        draw_rect_filled(200,SCREEN_H//2,380,SCREEN_H,(*C_DARK,220))
        arcade.draw_line(390,0,390,SCREEN_H,(*C_ACCENT,60),1)
        arcade.draw_text("CLOUT.EXE",20,SCREEN_H-40,C_ACCENT,28,bold=True,font_name="Courier New")
        arcade.draw_text("social media simulator",20,SCREEN_H-62,(*C_LIGHT,150),11,font_name="Courier New")
        arcade.draw_line(20,SCREEN_H-72,370,SCREEN_H-72,(*C_ACCENT,50),1)

        y=SCREEN_H-100
        self._draw_stat("FOLLOWERS",f"{int(self.followers):,}",y,C_ACCENT)
        self._draw_stat("TOTAL POSTS",str(self.total_posts),y-35,C_BLUE)
        self._draw_stat("TOTAL LIKES",f"{self.total_likes:,}",y-70,C_PINK)
        self._draw_stat("STREAK",f"{self.streak}🔥",y-105,C_YELLOW)

        ey=y-150
        arcade.draw_text("ENERGY",20,ey,C_LIGHT,10,font_name="Courier New")
        draw_rect_filled(195,ey+6,350,14,C_MID)
        bar_w=int(350*self.energy/100)
        ec=C_ACCENT if self.energy>50 else(C_YELLOW if self.energy>20 else C_RED)
        if bar_w>0: draw_rect_filled(20+bar_w//2,ey+6,bar_w,12,ec)
        arcade.draw_text(f"{int(self.energy)}%",330,ey,C_LIGHT,10,font_name="Courier New")

        ty=ey-50
        arcade.draw_text("SELECT POST TYPE:",20,ty,C_LIGHT,10,font_name="Courier New")
        self._refresh_available()
        for i,pt in enumerate(self.available_types):
            cfg=POST_CONFIG[pt]; sel=(i==self.selected_type_idx%len(self.available_types))
            bx,by=20+(i%3)*120,ty-30-(i//3)*45
            col=cfg["color"] if sel else C_MID
            draw_rect_filled(bx+55,by+15,108,36,(*col,180 if sel else 60))
            if sel: draw_rect_outline(bx+55,by+15,108,36,col,2)
            arcade.draw_text(f"{cfg['emoji']} {pt.value}",bx+5,by+5,C_WHITE if sel else C_LIGHT,9,font_name="Courier New")

        qt_y=ty-30-((len(self.available_types)-1)//3+1)*45-20
        arcade.draw_text("POST QUALITY:",20,qt_y,C_LIGHT,10,font_name="Courier New")
        for i,label in enumerate(QUALITY_LABELS):
            bx=20+i*68; sel=(i==self.selected_quality)
            col=[C_RED,C_RED,C_YELLOW,C_ACCENT,C_PURPLE][i]
            draw_rect_filled(bx+30,qt_y-20,60,28,(*col,180 if sel else 50))
            if sel: draw_rect_outline(bx+30,qt_y-20,60,28,col,2)
            arcade.draw_text(label,bx+4,qt_y-28,C_WHITE,9,font_name="Courier New")

        if self.available_types:
            pt=self.available_types[self.selected_type_idx%len(self.available_types)]
            cfg=POST_CONFIG[pt]
            vc=max(0.05,min(0.95,cfg["viral"]+(self.selected_quality-2)*0.10+min(self.streak*0.03,0.15)))
            rc=cfg["ratio_risk"]+(4-self.selected_quality)*0.05
            vc_y=qt_y-60
            arcade.draw_text(f"viral chance:  {vc*100:.0f}%",20,vc_y,C_ACCENT,10,font_name="Courier New")
            arcade.draw_text(f"ratio risk:    {rc*100:.0f}%",20,vc_y-18,C_RED,10,font_name="Courier New")

        pb_y=80; flash=self.posting_anim
        btn_color=tuple(min(255,int(c+(255-c)*flash*0.5)) for c in C_ACCENT)
        draw_rect_filled(195,pb_y,350,50,(*btn_color,220))
        draw_rect_outline(195,pb_y,350,50,C_ACCENT,2)
        arcade.draw_text("[ PRESS SPACE TO POST ]",30,pb_y-9,C_DARK,14,bold=True,font_name="Courier New")
        arcade.draw_text("← → change type  |  ↑ ↓ quality",20,30,(*C_LIGHT,120),9,font_name="Courier New")

    def _draw_stat(self,label,value,y,color):
        arcade.draw_text(label,20,y,(*C_LIGHT,160),9,font_name="Courier New")
        arcade.draw_text(value,200,y,color,18,bold=True,font_name="Courier New")

    def _draw_right_panel(self):
        draw_rect_filled(720,SCREEN_H//2,220,SCREEN_H,(*C_DARK,160))
        arcade.draw_line(610,0,610,SCREEN_H,(*C_ACCENT,40),1)
        arcade.draw_text("STATS",625,SCREEN_H-40,C_ACCENT,14,bold=True,font_name="Courier New")

        arcade.draw_text("FOLLOWER CURVE",625,SCREEN_H-70,C_LIGHT,9,font_name="Courier New")
        graph_h=80; graph_y0=SCREEN_H-160
        draw_rect_filled(720,graph_y0+graph_h//2,180,graph_h,C_MID)
        if self.feed_items:
            points=[]; n=min(len(self.feed_items),10); running=self.followers
            for i,fi in enumerate(reversed(list(self.feed_items)[:n])):
                x=625+i*(180//max(n,1))
                running_norm=min(1.0,running/max(1,self.followers+100))
                points.append((x,graph_y0+int(running_norm*graph_h*0.9)))
                running=max(0,running-fi.record.followers_gained)
            if len(points)>=2: arcade.draw_line_strip(points,C_ACCENT,2)

        arcade.draw_text("BEST POST:",625,SCREEN_H-250,C_LIGHT,9,font_name="Courier New")
        if self.best_post:
            bp=self.best_post; cfg=POST_CONFIG[bp.post_type]
            arcade.draw_text(f"{cfg['emoji']} {bp.post_type.value}",625,SCREEN_H-268,cfg["color"],12,bold=True,font_name="Courier New")
            arcade.draw_text(f"{bp.likes:,} likes",625,SCREEN_H-285,C_PINK,10,font_name="Courier New")
            arcade.draw_text(f"+{bp.followers_gained:,} followers",625,SCREEN_H-300,C_ACCENT,10,font_name="Courier New")
        else:
            arcade.draw_text("post something!",625,SCREEN_H-268,(*C_LIGHT,100),10,font_name="Courier New")

        arcade.draw_text("UPCOMING UNLOCKS:",625,SCREEN_H-340,C_LIGHT,9,font_name="Courier New")
        shown=0
        for pt,cfg in POST_CONFIG.items():
            if cfg["unlock"]>self.followers and shown<3:
                arcade.draw_text(f"{cfg['emoji']} {pt.value} @ {int(cfg['unlock'])} (+{int(cfg['unlock']-self.followers)})",
                                 625,SCREEN_H-358-shown*18,(*C_LIGHT,140),9,font_name="Courier New"); shown+=1

        arcade.draw_text("HOW IT WORKS:",625,SCREEN_H-460,C_YELLOW,9,bold=True,font_name="Courier New")
        for i,tip in enumerate(["• viral chance = base + quality","  bonus + streak bonus",
                                 "• quality ↑ = more followers","• hot takes = high risk/reward",
                                 "• random events every post","• 20 energy per post (regens)"]):
            arcade.draw_text(tip,625,SCREEN_H-478-i*16,(*C_LIGHT,140),8,font_name="Courier New")

    def _draw_feed(self):
        arcade.draw_text("FEED",415,SCREEN_H-40,C_ACCENT,14,bold=True,font_name="Courier New")
        arcade.draw_line(400,SCREEN_H-52,600,SCREEN_H-52,(*C_ACCENT,50),1)
        for fi in self.feed_items[:6]:
            rec=fi.record; cfg=POST_CONFIG[rec.post_type]; bx,by=400+fi.slide_x,fi.y
            draw_rect_filled(bx+100,by-28,210,62,(*C_MID,180))
            draw_rect_outline(bx+100,by-28,210,62,cfg["color"],1)
            arcade.draw_text(f"{cfg['emoji']} {rec.post_type.value.upper()}",bx+5,by-14,cfg["color"],10,bold=True,font_name="Courier New")
            arcade.draw_text(QUALITY_LABELS[rec.quality],bx+155,by-14,[C_RED,C_RED,C_YELLOW,C_ACCENT,C_PURPLE][rec.quality],9,font_name="Courier New")
            arcade.draw_text(f"❤️ {rec.likes:,}  🔁 {rec.shares:,}",bx+5,by-30,C_LIGHT,9,font_name="Courier New")
            sign="+" if rec.followers_gained>=0 else ""
            arcade.draw_text(f"{sign}{rec.followers_gained:,} followers",bx+5,by-47,
                             C_ACCENT if rec.followers_gained>=0 else C_RED,9,bold=True,font_name="Courier New")

    def _draw_particles(self):
        for p in self.particles:
            arcade.draw_circle_filled(p.x,p.y,p.size*(p.life/p.max_life),(*p.color,int(255*p.life/p.max_life)))

    def _draw_notifications(self):
        for i,n in enumerate(reversed(self.notifications)):
            arcade.draw_text(n["msg"],SCREEN_W//2-150,SCREEN_H-80-i*28,
                             (*n["color"],min(255,int(n["timer"]/3.0*255))),13,bold=True,font_name="Courier New")

    def _draw_event_banner(self):
        if not self.active_event: return
        ev=self.active_event
        alpha=int(180*(0.7+0.3*math.sin(self.total_time*8))*min(1.0,self.event_timer))
        draw_rect_filled(SCREEN_W//2,50,SCREEN_W,40,(*ev["color"],alpha//2))
        arcade.draw_text(ev["msg"],SCREEN_W//2-200,42,ev["color"],16,bold=True,font_name="Courier New")

    def on_key_press(self,key,modifiers):
        n=max(1,len(self.available_types))
        if key==arcade.key.SPACE: self.post_content()
        elif key==arcade.key.RIGHT: self.selected_type_idx=(self.selected_type_idx+1)%n
        elif key==arcade.key.LEFT:  self.selected_type_idx=(self.selected_type_idx-1)%n
        elif key==arcade.key.UP:    self.selected_quality=min(4,self.selected_quality+1)
        elif key==arcade.key.DOWN:  self.selected_quality=max(0,self.selected_quality-1)
        elif key==arcade.key.R:     self.setup()


def main():
    game=SocialMediaGame()
    arcade.run()

if __name__=="__main__":
    main()
