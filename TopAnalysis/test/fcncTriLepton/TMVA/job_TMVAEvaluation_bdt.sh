#!/bin/bash

#channel=( "TTZct TTZut STZct STZut" )
channel=( "TTZct STZct" )
mode=( "ElElEl MuElEl ElMuMu MuMuMu" )

for ch in ${channel[@]}; do
    for mo in ${mode[@]}; do
        nohup python TMVAEvaluation_bdt.py ${ch} ${mo} > log_eval_${ch}_${mo}.txt &
    done
done

