from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate
from auth import CurrentUser

router = APIRouter()

################# API(posts) #################
@router.get("", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    stmt = (
        select(models.Post)
        .options(joinedload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
    )
    result = await db.execute(stmt)
    posts = result.scalars().unique().all()
    return posts


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: PostCreate,
    current_user:CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    stmt = (
        select(models.Post)
        .where(models.Post.id == post_id)
        .options(joinedload(models.Post.author))
    )
    result = await db.execute(stmt)
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post not found"
        )
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(
        post_id: int,
        post_date: PostCreate,
        current_user:CurrentUser,
        db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = (
        select(models.Post)
        .where(models.Post.id == post_id)
        .options(joinedload(models.Post.author))
    )
    result = await db.execute(stmt)
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post not found"
        )
        
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )
        
    post.title = post_date.title
    post.content = post_date.content
    
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = (
        select(models.Post)
        .where(models.Post.id == post_id)
        .options(joinedload(models.Post.author))
    )
    result = await db.execute(stmt)
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    update_data = post_data.model_dump(exclude_unset=True)
            
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post

    
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    post = await db.get(models.Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
        
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    await db.delete(post)
    await db.commit()
    
    return None