const {exec} = require('child_process');
const express=require("express");
const fs=require("fs");
const app=express();

app.get('/article',async (req,res)=>{
    try{
    let query=req.query;
    fs.writeFileSync(__dirname+"/configs/article.json",JSON.stringify(query));
    let result=await executeLamda('python-lambda-local -f lambda_handler ../Article.py ./configs/article.json -e ./configs/env.json');
    res.send({result:result})}
    catch(err){
        res.send({error:err.message})
    }
})

app.get('/sectionpage',async (req,res)=>{
    try{
    let query=req.query;
    fs.writeFileSync(__dirname+"/configs/sectionpage.json",JSON.stringify(query));
    let result=await executeLamda('python-lambda-local -f lambda_handler ../SectionPage.py ./configs/sectionpage.json -e ./configs/env.json');
    res.send({result:result})
    }catch(err){
        res.send({error:err.message})
    }
})

app.get('/media',async (req,res)=>{
    try{
    let query=req.query;
    fs.writeFileSync(__dirname+"/configs/media.json",JSON.stringify(query));
    let result=await executeLamda('python-lambda-local -f lambda_handler ../Media.py ./configs/media.json -e ./configs/env.json');
    res.send({result:result})
    }catch(err){
        res.send({error:err.message})
    }
})

function executeLamda(command){
    return new Promise((resolve,rej)=>{
        exec(command,(code, stdout, stderr)=> {
        try{
            let op=""
            if(stdout.indexOf("{'omniture'")!=-1) op=stdout;
            else if(stderr.indexOf("{'omniture'")!=-1) op=stderr;
            let resultIndex=op.indexOf("{'omniture'")
            let resultIndexEnd=op.lastIndexOf('}}')
            op=op.slice(resultIndex,resultIndexEnd+2);            
            // stdout=stdout.slice(0,-2);
            op=op.replace(/'/g,String.fromCharCode(34))
            op=op.replace(/""/g,String.fromCharCode(34))
            resolve(JSON.parse(op))
        }
        catch(err){
            rej({error:err.message})
        }
    });    
    })
}

app.listen(3000,()=>{console.log("Server Running at http://localhost:3000")})

