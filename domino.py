from numba import cuda
from numba.typed import List
from numba import jit,njit,prange
import numpy as np
#@cuda.jit
@jit(nopython=True,parallel=True)
def calc_one_depth(ki,situationslist,mysitutations,scores,jprops,first,sides,jmprops,opppieces,ib):
 for j in prange(len(mysitutations)):
  if len(sides)>j:
    side=sides[j]
    situations=situationslist[j]
    def getavailable(boardline,pieces,ppieces,props):
        i=0
        for p in pieces:
            if p[0]==boardline or p[1]==boardline and props[i]!=0.:
                ppieces[i]=1
            i+=1
    def rewardevaluate(props,pieces,mypieces):
        sum=0.0
        i=0
        for p in pieces:
            sum+=(p[0]+0.+p[1]+0.)*props[i]
            i+=1
        for m in mypieces:
            sum-=m[0]+0.+m[1]+0.
        return sum
    #
    mysit=mysitutations[j]
    numofp=mysit[1][0]
    numofplayed=mysit[2][0]
    numofp=int(numofp)
    numofplayed=int(numofplayed)
    mypiece=mysit[3+ki]
    mypiecess=mysit[3:3+numofp]
    boardline0=mysit[3+numofp][0]
    boardline1=mysit[3+numofp][1]
    if numofplayed!=0:
       playedpieces=mysit[3+numofp+1:3+numofp+1+numofplayed]
    numofevaded=mysit[3+numofp+1+numofplayed][0]
    numofevaded=int(numofevaded)
    if numofevaded!=0:
       evades=mysit[3+numofp+2+numofplayed:3+numofp+2+numofplayed+numofevaded]
    oppnum=mysit[3+numofp+2+numofplayed+numofevaded][0]
    #opppieces=mysit[3+numofp+3+numofplayed+numofevaded:3+numofp+3+numofplayed+numofevaded+28]
    #
    props=jprops[j]
    mprops=jmprops[j]
    mainsc=-1000.
    vr=0
    if first:
        boardline0=mypiece[0]
        boardline1=mypiece[1]
    if True:
        boardline=0
        if ib==0:
            boardline=boardline0
            boardlines=boardline1
        else:
            boardline=boardline1
            boardlines=boardline0
        n=False
        if mypiece[0]==boardline or mypiece[1]==boardline or first:
            n=True
        if True:
         if first:
            boardline=mypiece[ib]
         else:
             if mypiece[0]==boardline:
                 boardline=mypiece[1]
             else:
                 boardline=mypiece[0]
         pl=0.
         pl2=0.
         if numofplayed!=0:
           for hp in playedpieces:
             if hp[0]==boardline or hp[1]==boardline:
                 pl+=1.
         for hp in mypiecess:
             if hp[0]==boardline or hp[1]==boardline:
                 pl+=1.
         allv=28-numofp-numofplayed
         pl=7.-pl
         pl2=7.-pl2
         myprop=0.
         myprop2=0.
         myprop=oppnum/allv
         myprop2=oppnum/allv
         for i in range(len(props)):
            v=False
            vf=False
            if opppieces[i][0]==boardline or opppieces[i][1]==boardline :
                v=True
                if numofevaded!=0:
                   for k in evades:
                      if opppieces[i][0]==k[0] or opppieces[i][0]==k[1] or opppieces[i][1]==k[0] or opppieces[i][1]==k[1]:
                          v=False
                          break
                if v:
                    for u in mypiecess:
                        if opppieces[i][0]==u[0] and opppieces[i][1]==u[1]:
                            v=False
                            break
                if v and numofplayed !=0:
                    for u in playedpieces:
                        if opppieces[i][0]==u[0] and opppieces[i][1]==u[1]:
                            v=False
                            break
            if opppieces[i][0]==boardlines or opppieces[i][1]==boardlines :
                vf=True
                if numofevaded!=0:
                   for k in evades:
                      if opppieces[i][0]==k[0] or opppieces[i][0]==k[1] or opppieces[i][1]==k[0] or opppieces[i][1]==k[1]:
                          vf=False
                          break
                if vf:
                    for u in mypiecess:
                        if opppieces[i][0]==u[0] and opppieces[i][1]==u[1]:
                            vf=False
                            break
                if vf and numofplayed !=0:
                    for u in playedpieces:
                        if opppieces[i][0]==u[0] and opppieces[i][1]==u[1]:
                            vf=False
                            break
            if vf:
                props[i]=myprop2
            if v:
                props[i]=myprop
            elif vf==False and v==False:
                props[i]=0.

            ghv=oppnum/allv
            if True:
                v=True
                if numofevaded!=0:
                   for k in evades:
                      if opppieces[i][0]==k[0] or opppieces[i][0]==k[1] or opppieces[i][1]==k[0] or opppieces[i][1]==k[1]:
                          v=False
                          break
                if v:
                    for u in mypiecess:
                        if opppieces[i][0]==u[0] and opppieces[i][1]==u[1]:
                            v=False
                            break
                if v and numofplayed !=0:
                    for u in playedpieces:
                        if opppieces[i][0]==u[0] and opppieces[i][1]==u[1]:
                            v=False
                            break
            if v:
                mprops[i]=ghv
            else:
                mprops[i]=0.
        score=rewardevaluate(mprops,opppieces,mypiecess)
        mainsc=score-100
        if numofp==1 and n:
            mainsc=score+100
            n=False
        if n:
         score=score+mypiece[0]+mypiece[1]
         s=score+1
         #تعبئة المواقف و حساب المكافآت
         for i in range(len(mprops)):
             sc=(score-(opppieces[i][0]+opppieces[i][1])*mprops[i])*props[i]
             if props[i]!=0 and numofp>1. :
               for ib2 in range(0,2):
                if (ib2==0 and (opppieces[i][0]==boardline or opppieces[i][1]==boardline)) or (ib2==1 and (opppieces[i][0]==boardlines or opppieces[i][1]==boardlines)):
                 if oppnum==1:
                     sc-=100
                     if sc<s:
                         s=sc
                     break
                 mysnsit=situations[vr]
                 mysnsit[0][0]=1.;mysnsit[0][1]=mysit[0][1]*props[i]+0.
                 mysnsit[1][0]= mysit[1][0]-1
                 mysnsit[2][0]=mysit[2][0]+2
                 #mysit[3:3+numofp]
                 hg=0
                 for tracker in range(3,3+numofp):
                     if tracker!=ki+3:
                        mysnsit[tracker-hg][0]=mysit[tracker][0]+0.;mysnsit[tracker-hg][1]=mysit[tracker][1]+0.;
                     else:
                         hg=1
                 mysnsit[3+numofp-hg][0]=boardline+0.
                 mysnsit[3+numofp-hg][1]=boardlines+0.
                 if ib2==0:
                    if opppieces[i][0]==boardline:
                        mysnsit[3+numofp-hg][ib2]=opppieces[i][1]+0.
                    elif opppieces[i][1]==boardline:
                        mysnsit[3+numofp-hg][ib2]=opppieces[i][0]+0.
                 else:
                    if opppieces[i][0]==boardlines:
                        mysnsit[3+numofp-hg][ib2]+=opppieces[i][1]+0.
                    elif opppieces[i][1]==boardlines:
                        mysnsit[3+numofp-hg][ib2]+=opppieces[i][0]+0.
                    #mysnsit[3+numofp-hg][ib]=boardlines+0.
                 #mysit[3+numofp+1:3+numofp+1+numofplayed]
                 
                 for tracker in range(3+numofp+1,3+numofp+3+numofplayed):
                     mysnsit[tracker-hg][0]=mysit[tracker][0]+0.;mysnsit[tracker-hg][1]=mysit[tracker][1]+0.;
                     if tracker-hg==3+numofp+numofplayed:
                         mysnsit[tracker-hg][0]=mypiece[0]+0.;mysnsit[tracker-hg][1]=mypiece[1]+0.
                     elif tracker-hg==3+numofp+numofplayed+1:
                         mysnsit[tracker-hg][0]=opppieces[i][0]+0.;mysnsit[tracker-hg][1]=opppieces[i][1]+0.
                 mysnsit[3+numofp+2+numofplayed][0]=mysit[3+numofp+1+numofplayed][0]+0.
                 if numofevaded!=0:
                    for tr in range(3+numofp-1+2+numofplayed,3+numofp-1+2+numofplayed+numofevaded):
                       mysnsit[tr][0]=mysit[tr-2][0]
                       mysnsit[tr][1]=mysit[tr-2][1]
                 mysnsit[3+numofp+2+numofplayed+numofevaded+2-1][0]=oppnum-1.
                 vr+=1
               if sc<s:
                    s=sc
         #if s>mainsc or True:
         mainsc=s
         side[0]=ib
    scores[j][0]=mainsc*mysit[0][1]
    if mainsc<99:
        []
    []
@jit
def selector(situationslist,mypiece,numofp):
    stl=List()
    for ij1 in range(len(situationslist)):
        fgh=situationslist[ij1]
        for ijk in range(len(fgh)):
            if fgh[ijk][0][0]==1.:
                boardline0=fgh[ijk][3+numofp][0]
                boardline1=fgh[ijk][3+numofp][1]
                if mypiece[0]==boardline0 or mypiece[0]==boardline1 or mypiece[1]==boardline0 or mypiece[1]==boardline1:
                   stl.append(fgh[ijk])
    return stl
@jit
def selectworest(scores,sides):
    ans=10**8
    w=0
    side=0
    for i in range(len(scores)):
        if scores[i][0]<ans:
            ans=scores[i][0]
            side=sides[i][0]
            w=i
    return w,side ,ans
def go(mysitutation,bb):
       mysit=mysitutation
       numofp=mysit[1][0]
       numofp2=int(numofp+1)
       numofplayed=mysit[2][0]
       numofp=int(numofp)
       numofplayed=int(numofplayed)
       mypiecess=mysit[3:3+numofp]
       #boardline0=mysit[3+numofp][0]
       #boardline1=mysit[3+numofp][1]
       if numofplayed!=0:
          playedpieces=mysit[3+numofp+1:3+numofp+1+numofplayed]
       numofevaded=mysit[3+numofp+1+numofplayed][0]
       numofevaded=int(numofevaded)
       if numofevaded!=0:
          evades=mysit[3+numofp+2+numofplayed:3+numofp+2+numofplayed+numofevaded]
       oppnum=mysit[3+numofp+2+numofplayed+numofevaded][0]
       if True:
                 mysnsit=np.copy(mysitutation)
                 mysnsit[0][0]=1.;mysnsit[0][1]=1.
                 mysnsit[1][0]= mysit[1][0]+1.
                 #mysit[3:3+numofp]
                 hg=0
                 for tracker in range(3,3+numofp2):
                     if tracker != numofp2+2:
                        mysnsit[tracker][0]=mysit[tracker][0]+0.;mysnsit[tracker][1]=mysit[tracker][1]+0.;
                     else:
                         mysnsit[tracker][0]=bb[0]+0.;mysnsit[tracker][1]=bb[1]+0.
                 #3+numofp+2+numofplayed+numofevaded
                 for tracker in range(3+numofp2,len(mysit)-1):
                     mysnsit[tracker][0]=mysit[tracker-1][0]+0.;mysnsit[tracker][1]=mysit[tracker-1][1]+0.;
       return mysnsit

def main():
    mysitutation=np.array([[1,1],[7,0],[0,0],   [3,3],[0,1],[5,6],[2,2],[2,3],[0,4],[3,6]  ,[0,0],[0,0],[7,0],[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [3, 3], [3, 4], [3, 5], [3, 6], [4, 4], [4, 5], [4, 6], [5, 5], [5, 6], [6, 6],[1,5],[2,4],[0,2],[0,5],[2,5],[1,3],[3,4]  ,[0,0],[0,0],[7,0],[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [3, 3], [3, 4], [3, 5], [3, 6], [4, 4], [4, 5], [4, 6], [5, 5], [5, 6], [6, 6]],dtype=float)
    props=np.array([0.]*28)
    mprops=np.array([0.]*28)
    situationslist=np.array([np.array([np.array([[0,0]]*200)]*160)]*1000)
    scores=np.array([[0.]]*10000)
    sides=np.array([[0]]*10000)
    opppieces=np.array([[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [3, 3], [3, 4], [3, 5], [3, 6], [4, 4], [4, 5], [4, 6], [5, 5], [5, 6], [6, 6]])
    #calc_one_depth(0,situationslist,np.array([mysitutation]*10000),scores,np.array([props]*10000),True,sides,np.array([mprops]*10000),opppieces)
    first=True;boardline0=0.;boardline1=0.;
    dr=3
    while True:
     if True:
       if not first:
           dr=12
       bestp,side,ans,dragpass,_=calcevaluations(np.array([np.copy(mysitutation)]),opppieces,first,dr)
       numofp=mysitutation[1][0]
       numofp=int(numofp)
       boardline0=mysitutation[3+numofp][0]
       boardline1=mysitutation[3+numofp][1]
       numofplayed=mysitutation[2][0]
       numofplayed=int(numofplayed)
       numofevaded=mysitutation[3+numofp+1+numofplayed][0]
       numofevaded=int(numofevaded)
       oppnum=mysitutation[3+numofp+2+numofplayed+numofevaded][0]
       if not dragpass :
           print("put piece ",bestp," : ",ans ,"in side ",side)
       else:
           while dragpass:
               if oppnum+numofplayed+numofp<28:
                   print("drag piece !")
                   g=input("piece 0 : ")
                   g2=input("piece 1  : ")
                   g=int(g);g2=int(g2)
                   bb=0
                   for j in opppieces:
                       if (j[0]==g and j[1]==g2) or (j[0]==g2 and j[1]==g):
                            bb=j
                   mysit=mysitutation
                   numofp=mysit[1][0]
                   numofp+=1
                   mysitutation=go(mysitutation,bb)
                   bestp,side,ans,dragpass,_=calcevaluations(np.array([np.copy(mysitutation)]),opppieces,first,dr)
                   if not dragpass :
                       print("put piece ",bestp," : ",ans ,"in side ",side)
               else:
                   print("pass ! ")
                   break
     tu=int(input(" 0 if you played 1 if you passed 2 if you dragged : "))
     if tu==2:
         tu=0
         nofvs=int(input("num of pieces dragged : "))
         #if nofvs==1:
         mysit=mysitutation
         numofp=mysit[1][0]
         numofplayed=mysit[2][0]
         numofp=int(numofp)
         numofplayed=int(numofplayed)
         numofevaded=mysit[3+numofp+1+numofplayed][0]
         mysit[3+numofp+1+numofplayed][0]+=1
         numofevaded+=1
         numofevaded=int(numofevaded)
         mysit[3+numofp+2+numofplayed+numofevaded][0]+=nofvs
         if numofevaded!=0:
                for tracker in range(3+numofp-1+2+numofplayed+2,3+numofp-1+2+numofplayed+numofevaded+3):
                    if tracker !=3+numofp-1+2+numofplayed+numofevaded+2 and nofvs==1:
                       mysit[tracker]=mysitutation[tracker]
                    else:
                       mysit[tracker]=np.array([boardline0+0.,boardline1+0.])
         tu=int(input("did you play ? 0,1:"))
         mysitutation=mysit
       #if tu= =0:
     if tu==0 or tu==1:
       g=int(input("opponent response 0: "))
       g2=int(input("opponent response 1: "))
       bb=0

       for j in opppieces:
           if (j[0]==g and j[1]==g2) or (j[0]==g2 and j[1]==g):
                   bb=j
       if side ==0 and dragpass==False:
           if bestp[0]==boardline0 :
              boardline0=bestp[1]
           else:
              boardline0=bestp[0]
       if side ==1 and dragpass==False:
           if bestp[0]==boardline1 :
              boardline1=bestp[1]
           else:
              boardline1=bestp[0]
       if first:
           boardline0=bestp[0];boardline1=bestp[1]
       first=False
       t=int(input("side: "))
       mysit=mysitutation
       numofp=mysit[1][0]
       numofplayed=mysit[2][0]
       numofp=int(numofp)
       numofplayed=int(numofplayed)
       mypiece=bestp
       mypiecess=mysit[3:3+numofp]
       #boardline0=mysit[3+numofp][0]
       #boardline1=mysit[3+numofp][1]
       if numofplayed!=0:
          playedpieces=mysit[3+numofp+1:3+numofp+1+numofplayed]
       numofevaded=mysit[3+numofp+1+numofplayed][0]
       numofevaded=int(numofevaded)
       if numofevaded!=0:
          evades=mysit[3+numofp+2+numofplayed:3+numofp+2+numofplayed+numofevaded]
       oppnum=mysit[3+numofp+2+numofplayed+numofevaded][0]
       boardline=boardline0
       boardlines=boardline1
       ib=t
       if True:
                 mysnsit=np.copy(mysitutation)
                 mysnsit[0][0]=1.;mysnsit[0][1]=1.
                 mysnsit[1][0]= mysit[1][0]-1
                 mysnsit[2][0]=mysit[2][0]+2
                 #mysit[3:3+numofp]
                 hg=0
                 for tracker in range(3,3+numofp):
                     if mysit[tracker][0]!=bestp[0] or mysit[tracker][1]!=bestp[1]:
                        mysnsit[tracker-hg][0]=mysit[tracker][0]+0.;mysnsit[tracker-hg][1]=mysit[tracker][1]+0.;
                     else:
                         hg=1
                 #3+numofp+2+numofplayed+numofevaded
                 mysnsit[3+numofp-hg][0]=boardline+0.
                 mysnsit[3+numofp-hg][1]=boardlines+0.
                 if ib==0 and tu==0:
                    if bb[0]==boardline:
                        mysnsit[3+numofp-hg][ib]=bb[1]+0.
                    elif bb[1]==boardline:
                        mysnsit[3+numofp-hg][ib]=bb[0]+0.
                 elif tu==0:
                    if bb[0]==boardlines:
                        mysnsit[3+numofp-hg][ib]=bb[1]+0.
                    elif bb[1]==boardlines:
                        mysnsit[3+numofp-hg][ib]=bb[0]+0.
                    #mysnsit[3+numofp-hg][ib]=boardlines+0.
                 #mysit[3+numofp+1:3+numofp+1+numofplayed]
                 
                 for tracker in range(3+numofp+1,3+numofp+2+(1-tu)+numofplayed):
                     mysnsit[tracker-hg][0]=mysit[tracker][0]+0.;mysnsit[tracker-hg][1]=mysit[tracker][1]+0.;
                     if tracker-hg==3+numofp+numofplayed:
                         mysnsit[tracker-hg][0]=mypiece[0]+0.;mysnsit[tracker-hg][1]=mypiece[1]+0.
                     elif tracker-hg==3+numofp+numofplayed+1:
                         mysnsit[tracker-hg][0]=bb[0]+0.;mysnsit[tracker-hg][1]=bb[1]+0.
                 mysnsit[3+numofp+2+numofplayed][0]=mysit[3+numofp+1+numofplayed][0]+0.
                 if numofevaded!=0:
                    mysnsit[3+numofp-1+2+numofplayed+2:3+numofp-1+2+numofplayed+numofevaded+1+(1-tu)]=mysit[3+numofp+2+numofplayed:3+numofp+2+numofplayed+numofevaded]
                 mysnsit[3+numofp+2+numofplayed+numofevaded+1+(1-tu)-1][0]=oppnum-(1-tu)
       mysitutation=mysnsit
    []

def calcevaluations(mysitutations,opppieces,first,depth):
    props=np.array([0.]*28)
    mprops=np.array([0.]*28)
    situationslist1=np.array([np.array([np.array([[0.,0.]]*200)]*30)]*len(mysitutations))
    scores1=np.array([[10000000.0]]*100000)
    sides1=np.array([[0]]*100000)
    #play=np.array([[0]]*10000)
    numofp=mysitutations[0][1][0]
    numofp=int(numofp)
    ans=-10**8
    w=0
    bestp=0
    side=0
    dragpass=False
    #if i==0:
    dragpass=True
    for i in range(numofp):
        drg=True
        for ib in range(2):
            if ib==1 and first:
                break
            situationslist=np.copy(situationslist1)
            scores=np.copy(scores1)
            sides=np.copy(sides1)
            [10,len(mysitutations)//10+10]
            #لا تنسى حل مشكلة فقدان القيمة المرجعية لقطع الخصم
            calc_one_depth(i,situationslist,mysitutations,scores,np.array([props]*len(mysitutations)),first,sides,np.array([mprops]*len(mysitutations)),opppieces,ib)
            stl=selector(situationslist,mysitutations[0][3+i],numofp)
            stl=np.array(stl,dtype=float)
            y=False
            if first:
                  dragpass=False
            else:
                   boardline0=mysitutations[0][3+numofp][0]
                   boardline1=mysitutations[0][3+numofp][1]
                   if (ib==0 and (mysitutations[0][3+i][0]==boardline0 or  mysitutations[0][3+i][1]==boardline0)) or (ib==1 and (mysitutations[0][3+i][0]==boardline1 or  mysitutations[0][3+i][1]==boardline1)):
                      dragpass=False
            if depth==0  or len(stl)==0 :
              if len(stl)!=0:
                  drg=False
              g,sd,a=selectworest(scores,sides)
              if depth==2:
                  []
              if a>=ans:
                ans=a
                bestp=mysitutations[0][3+i]
                side=ib
            else:
              best,sd,an,dg,dt=calcevaluations(stl,opppieces,False,depth-1)
              dragpass=False
              if not dg :
               if an>=ans :
                  ans=an
                  bestp=mysitutations[0][3+i]
                  side=ib
              else:
                  g,sd,a=selectworest(scores,sides)
                  ans=a
                  bestp=mysitutations[0][3+i]
                  side=ib
    return bestp,side,ans,dragpass,depth
main()