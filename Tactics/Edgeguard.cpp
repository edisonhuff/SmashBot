#include <cmath>
#include <math.h>

#include "Edgeguard.h"
#include "../Constants.h"
#include "../Chains/Nothing.h"
#include "../Chains/EdgeStall.h"
#include "../Chains/JumpCanceledShine.h"
#include "../Chains/GrabEdge.h"
#include "../Chains/EdgeAction.h"
#include "../Controller.h"

Edgeguard::Edgeguard(GameState *state) : Tactic(state)
{
    m_chain = NULL;
}

Edgeguard::~Edgeguard()
{
    delete m_chain;
}

void Edgeguard::DetermineChain()
{
	//If we're not in a state to interupt, just continue with what we've got going
	if((m_chain != NULL) && (!m_chain->IsInterruptible()))
	{
		m_chain->PressButtons();
		return;
	}

	//distance formula
	double distance = pow(std::abs(m_state->player_one_x - m_state->player_two_x), 2);
	distance += pow(std::abs(m_state->player_one_y - m_state->player_two_y), 2);
	distance = sqrt(distance);

    //If we're able to shine p1 right now, let's do that
    if(std::abs(distance) < FOX_SHINE_RADIUS)
    {
        //Are we in a state where we can shine?
        if(m_state->player_two_action == FALLING)
        {
            //Is the opponent in a state where they can get hit by shine?
            if(!m_state->player_one_invulnerable)
            {
                CreateChain(JumpCanceledShine);
                m_chain->PressButtons();
                return;
            }
        }
    }

    //If enemy is sliding onto edge or hanging from it, don't grab the edge
    if(m_state->player_one_action == SLIDING_OFF_EDGE ||
        m_state->player_one_action == EDGE_GETUP_QUICK ||
        m_state->player_one_action == EDGE_ATTACK_SLOW ||
        m_state->player_one_action == EDGE_ATTACK_QUICK ||
        m_state->player_one_action == EGDE_ROLL_SLOW ||
        m_state->player_one_action == EDGE_ROLL_QUICK ||
        m_state->player_one_action == EDGE_GETUP_SLOW ||
        m_state->player_one_action == EDGE_CATCHING ||
        m_state->player_one_action == EDGE_HANGING)
    {
        CreateChain(Nothing);
        m_chain->PressButtons();
        return;
    }

    //If we're still on the stage, see if it's safe to grab the edge
    if(m_state->player_two_on_ground)
    {
        
        CreateChain(GrabEdge);
        m_chain->PressButtons();
        return;
    }

    //Edgehog our opponent if they're UP-B'ing sweetspotted.
    //Grab the edge if we're still on the stage
    if(m_state->player_one_y < 50 && m_state->player_one_action == UP_B)
    {
        CreateChain2(EdgeAction, Controller::BUTTON_L);
        m_chain->PressButtons();
        return;
    }

    //Edgestall to kill time
    if(m_state->player_two_action == EDGE_CATCHING ||
        m_state->player_two_action == EDGE_HANGING)
    {
        CreateChain(EdgeStall);
        m_chain->PressButtons();
        return;
    }

    //Just hang out and do nothing
    CreateChain(Nothing);
    m_chain->PressButtons();
    return;
}
