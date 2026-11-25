import matplotlib.pyplot as p
fig,ax=p.subplots(figsize=(10,5)); names=['Игрок','NavalUI','Battle','Weapon','Board','TacticalAI']; ax.set_xlim(-.6,5.6);ax.set_ylim(10,0);ax.axis('off')
for i,n in enumerate(names):
 ax.text(i,.5,n,ha='center',bbox=dict(facecolor='#e1edf5',edgecolor='#345'));ax.plot([i,i],[1,9.5],'--',color='#888',lw=.8)
for y,a,b,s in [(1.5,0,1,'клик'),(2.3,1,2,'play()'),(3.1,2,3,'attack()'),(3.9,3,4,'fire() [1–9 клеток]'),(4.7,4,3,'результаты'),(5.5,3,2,'результаты'),(6.3,2,5,'choose_shot()¹'),(7.1,5,2,'координата'),(7.9,2,4,'fire()¹ (поле игрока)'),(8.7,2,1,'результат хода'),(9.3,1,0,'обновление экрана')]:
 ax.annotate('',(b,y),(a,y),arrowprops=dict(arrowstyle='->',color='#234'));ax.text((a+b)/2,y-.12,s,ha='center',fontsize=8)
fig.text(.5,.02,'¹ Только если флот противника ещё не уничтожен.',ha='center',fontsize=9);fig.savefig('sequence.png',dpi=180,bbox_inches='tight')
