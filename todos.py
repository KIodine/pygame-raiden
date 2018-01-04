'''TODO
    Pyden todo list.

    Priority: 0 > 1 > 2 ...

    1. Menu #0
        Form:
            Start
            Rank
            Quit
        psuedo code:
            def menu():
                while Menu:
                    (some operation...)
                    if condition:
                        main()
                    elif condition2:
                        rank()
                (terminate...)
            return

            if __name__ == '__main__':
                menu()

            pygame.quit()
            sys.exit(0)

    2. Skill module #2
        Create skill module before instanitiate
        psuedo code:
            mob_skills = skill.Module(
                SkillID: Skillfunc
                ...
            )
            Mob(
                ...,
                skills=mob_skills
            )

    3. Independent motion control #1
        psuedo code:
            character.Motion(
                group=...
            )

    4. Sound effect #0
        Choose sound effect for actions.

    5. Timeline and event trigger #1
        event = timeline.Event(
            time,
            operation # Use functools.partial(...) to preform function.
        )
        event = timeline.Conditional(
            cond, # or operation.
            operation
        )
        trigger = timeline.Timeline.(events)
        trigger.add(events)
        trigger.start()

    6. background #0
        Choose images for background.

    7. Add 'spawn_at()' to 'MobHandle' #0
        ...
    
    8. Rank #0
        Form:
            #n      name    score
            #n-1    ...     ...
            ...     
            #n-10   ...     ...
            
    9. Fade out/in while phase change #0
'''
