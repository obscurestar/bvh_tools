
        if self.parent is None: 
            self.w_position = glm.vec3( 0, 0, 0 )
        else:
            self.w_position = self.parent.w_position + self.position

        if len(self.children) > 0:
            center = glm.vec3(0,0,0)

            for child in self.children:
                center = center + child.position

                #Bad form doing this here instead of its own loop.
                child.simplify_world_position( )

            self.w_end_position = center/len(self.children)
        else:
            self.w_end_position = self.end_position

        if self.w_end_position is None:
            self.w_end_position = glm.vec3( 0, 0, 0 )

        self.w_end_postion = self.w_end_position + self.w_position
